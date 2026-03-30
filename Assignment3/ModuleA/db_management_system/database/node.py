"""
Disk-Page Node Representations for the B+ Tree.

This module maps standard B+ Tree nodes (Leaves, Internals, Roots) directly onto 
fixed-size binary disk pages. Every Node class here knows exactly how to pack its 
Entries (Records or References) into a byte array, generate its own binary header, 
and pad itself out to the exact page size required by the database engine.
"""
import abc
import bisect
import math
from typing import Optional

from .const import (ENDIAN, NODE_TYPE_BYTES, USED_PAGE_LENGTH_BYTES,
                    PAGE_REFERENCE_BYTES, TreeConf)
from .entry import Entry, Record, Reference, OpaqueData


class Node(metaclass=abc.ABCMeta):
    """
    Abstract base class for all memory-mapped disk pages.
    It handles the low-level byte packing (dump) and unpacking (load) of page headers
    and standard entry payloads.
    """

    # Restricting attributes to save RAM when caching hundreds of nodes
    __slots__ = ['_tree_conf', 'entries', 'page', 'parent', 'next_page']

    # Subclasses must define these behavior flags
    _node_type_int = 0
    max_children = 0
    min_children = 0
    _entry_class = None

    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, parent: 'Node'=None, next_page: int=None):
        self._tree_conf = tree_conf
        self.entries = list()
        self.page = page
        self.parent = parent
        self.next_page = next_page
        
        # If raw disk bytes are provided, instantly parse them into this object
        if data:
            self.load(data)

    def load(self, data: bytes):
        """Unpacks a raw disk sector (byte array) into a structured Python Node."""
        assert len(data) == self._tree_conf.page_size, "Provided data chunk does not match database page size."
        
        # --- 1. Parse Page Header ---
        idx_used_size_end = NODE_TYPE_BYTES + USED_PAGE_LENGTH_BYTES
        active_page_length = int.from_bytes(
            data[NODE_TYPE_BYTES:idx_used_size_end], ENDIAN
        )
        
        idx_header_end = idx_used_size_end + PAGE_REFERENCE_BYTES
        self.next_page = int.from_bytes(
            data[idx_used_size_end:idx_header_end], ENDIAN
        )
        if self.next_page == 0:
            self.next_page = None

        if self._entry_class is None:
            # Marker nodes (like Freelist nodes) do not contain parseable entries
            return

        # --- 2. Determine Entry Boundaries ---
        try:
            # If the node holds fixed-width entries (like Records or References)
            step_size = self._entry_class(self._tree_conf).length
        except AttributeError:
            # If the node holds a single variable-width payload (like Overflow Data)
            step_size = active_page_length - idx_header_end

        # --- 3. Extract and Instantiate Entries ---
        for offset in range(idx_header_end, active_page_length, step_size):
            chunk = data[offset : offset + step_size]
            parsed_entry = self._entry_class(self._tree_conf, data=chunk)
            self.entries.append(parsed_entry)

    def dump(self) -> bytearray:
        """Serializes the Node back into a fixed-width binary page for disk storage."""
        payload_bytes = bytearray()
        
        # Pack all current entries sequentially
        for entry in self.entries:
            payload_bytes.extend(entry.dump())

        # Calculate exact header footprint: Type(1) + UsedLength(3) + NextPagePtr(4)
        header_size = 1 + 3 + PAGE_REFERENCE_BYTES
        total_active_bytes = len(payload_bytes) + header_size
        
        assert 0 < total_active_bytes <= self._tree_conf.page_size
        assert len(payload_bytes) <= self.max_payload

        # Construct the binary header
        target_next_page = 0 if self.next_page is None else self.next_page
        header_bytes = (
            self._node_type_int.to_bytes(1, ENDIAN) +
            total_active_bytes.to_bytes(3, ENDIAN) +
            target_next_page.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN)
        )

        # Combine header and payload
        full_page = bytearray(header_bytes) + payload_bytes

        # Pad the remainder of the page with null bytes to ensure rigid file structure
        empty_space = self._tree_conf.page_size - total_active_bytes
        assert empty_space >= 0
        full_page.extend(bytearray(empty_space))
        
        assert len(full_page) == self._tree_conf.page_size
        return full_page

    @property
    def max_payload(self) -> int:
        """Calculates the absolute byte limit available for entries on this page."""
        return self._tree_conf.page_size - 4 - PAGE_REFERENCE_BYTES

    @property
    def can_add_entry(self) -> bool:
        return self.num_children < self.max_children

    @property
    def can_delete_entry(self) -> bool:
        return self.num_children > self.min_children

    @property
    def smallest_key(self):
        return self.smallest_entry.key

    @property
    def smallest_entry(self):
        return self.entries[0]

    @property
    def biggest_key(self):
        return self.biggest_entry.key

    @property
    def biggest_entry(self):
        return self.entries[-1]

    @property
    def num_children(self) -> int:
        """The total number of operational items (entries/pointers) currently held."""
        return len(self.entries)

    def pop_smallest(self) -> Entry:
        """Removes and returns the leftmost entry (used during rebalancing)."""
        return self.entries.pop(0)

    def insert_entry(self, entry: Entry):
        """Uses binary insertion to keep the node's entries perfectly sorted."""
        bisect.insort(self.entries, entry)

    def insert_entry_at_the_end(self, entry: Entry):
        """An O(1) optimization for bulk-loading sorted data into the tree."""
        self.entries.append(entry)

    def remove_entry(self, key):
        target_idx = self._find_entry_index(key)
        self.entries.pop(target_idx)

    def get_entry(self, key) -> Entry:
        target_idx = self._find_entry_index(key)
        return self.entries[target_idx]

    def _find_entry_index(self, key) -> int:
        """
        Executes a rapid binary search (`bisect`) across the node's entries.
        Since entries implement comparison operators (__lt__, __eq__), bisect can 
        find the exact index without an O(n) linear scan.
        """
        search_probe = self._entry_class(
            self._tree_conf,
            key=key  
        )
        idx = bisect.bisect_left(self.entries, search_probe)
        if idx != len(self.entries) and self.entries[idx] == search_probe:
            return idx
        raise ValueError('No entry found for key: {}'.format(key))

    def split_entries(self) -> list:
        """
        Splits the node's entries precisely in half.
        The lower half remains in this node, and the upper half is returned 
        to be inserted into a newly allocated sibling node.
        """
        total_count = len(self.entries)
        midpoint = total_count // 2
        
        upper_half = self.entries[midpoint:]
        self.entries = self.entries[:midpoint]
        
        assert len(self.entries) + len(upper_half) == total_count
        return upper_half

    @classmethod
    def from_page_data(cls, tree_conf: TreeConf, data: bytes,
                       page: int=None) -> 'Node':
        """
        Factory method: Reads the first byte of a raw disk page to determine 
        its node type, then routes it to the correct specialized subclass.
        """
        type_indicator = int.from_bytes(data[0:NODE_TYPE_BYTES], ENDIAN)
        
        if type_indicator == 1:
            return LonelyRootNode(tree_conf, data, page)
        elif type_indicator == 2:
            return RootNode(tree_conf, data, page)
        elif type_indicator == 3:
            return InternalNode(tree_conf, data, page)
        elif type_indicator == 4:
            return LeafNode(tree_conf, data, page)
        elif type_indicator == 5:
            return OverflowNode(tree_conf, data, page)
        elif type_indicator == 6:
            return FreelistNode(tree_conf, data, page)
        else:
            assert False, 'Encountered corrupted or unknown Node type: {}'.format(type_indicator)

    def __repr__(self):
        return '<{}: page={} entries={}>'.format(
            self.__class__.__name__, self.page, len(self.entries)
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self.page == other.page and
            self.entries == other.entries
        )


# ==============================================================================
# LEAF LEVEL NODES (Data Storage)
# ==============================================================================

class RecordNode(Node):
    """Base class for nodes that store actual Key-Value Records."""
    __slots__ = ['_entry_class']

    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, parent: 'Node'=None, next_page: int=None):
        self._entry_class = Record
        super().__init__(tree_conf, data, page, parent, next_page)


class LonelyRootNode(RecordNode):
    """
    Type 1: A special transitional state where the tree only has a single node.
    It acts as both the Root (no parent) and a Leaf (stores actual records).
    """
    __slots__ = ['_node_type_int', 'min_children', 'max_children']

    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, parent: 'Node'=None):
        self._node_type_int = 1
        self.min_children = 0
        self.max_children = tree_conf.order - 1
        super().__init__(tree_conf, data, page, parent)

    def convert_to_leaf(self):
        """Transforms this node into a standard leaf when the tree grows."""
        new_leaf = LeafNode(self._tree_conf, page=self.page)
        new_leaf.entries = self.entries
        return new_leaf


class LeafNode(RecordNode):
    """
    Type 4: Standard leaf node. Forms the bottom linked-list layer of the B+ Tree.
    Contains the actual user data (or pointers to overflow pages).
    """
    __slots__ = ['_node_type_int', 'min_children', 'max_children']

    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, parent: 'Node'=None, next_page: int=None):
        self._node_type_int = 4
        # Standard B+ Tree property: nodes must be at least half full
        self.min_children = math.ceil(tree_conf.order / 2) - 1
        self.max_children = tree_conf.order - 1
        super().__init__(tree_conf, data, page, parent, next_page)


# ==============================================================================
# INTERNAL ROUTING NODES
# ==============================================================================

class ReferenceNode(Node):
    """Base class for nodes that store routing References instead of user data."""
    __slots__ = ['_entry_class']

    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, parent: 'Node'=None):
        self._entry_class = Reference
        super().__init__(tree_conf, data, page, parent)

    @property
    def num_children(self) -> int:
        """A Reference node has N entries, but N+1 child pointers."""
        return len(self.entries) + 1 if self.entries else 0

    def insert_entry(self, entry: 'Reference'):
        """
        Intercepts the standard insert to maintain contiguous page pointers.
        Ensures that the 'after' pointer of the previous reference matches 
        the 'before' pointer of the newly inserted reference.
        """
        super().insert_entry(entry)
        idx = self.entries.index(entry)
        
        # Stitch to the left neighbor
        if idx > 0:
            left_neighbor = self.entries[idx - 1]
            left_neighbor.after = entry.before
            
        # Stitch to the right neighbor
        try:
            right_neighbor = self.entries[idx + 1]
        except IndexError:
            pass
        else:
            right_neighbor.before = entry.after


class RootNode(ReferenceNode):
    """
    Type 2: The standard top-level routing node.
    It is allowed to have fewer children than standard internal nodes.
    """
    __slots__ = ['_node_type_int', 'min_children', 'max_children']

    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, parent: 'Node'=None):
        self._node_type_int = 2
        self.min_children = 2
        self.max_children = tree_conf.order
        super().__init__(tree_conf, data, page, parent)

    def convert_to_internal(self):
        """Demotes the root to an internal node when the tree grows upward."""
        internal = InternalNode(self._tree_conf, page=self.page)
        internal.entries = self.entries
        return internal


class InternalNode(ReferenceNode):
    """
    Type 3: Standard routing nodes that sit between the Root and the Leaves.
    """
    __slots__ = ['_node_type_int', 'min_children', 'max_children']

    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, parent: 'Node'=None):
        self._node_type_int = 3
        self.min_children = math.ceil(tree_conf.order / 2)
        self.max_children = tree_conf.order
        super().__init__(tree_conf, data, page, parent)


# ==============================================================================
# AUXILIARY STORAGE NODES
# ==============================================================================

class OverflowNode(Node):
    """
    Type 5: Specialized node for handling massive values.
    If a user inserts a value larger than `TreeConf.value_size`, it is chunked 
    and stored across a linked chain of these Overflow Nodes.
    """
    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, next_page: int=None):
        self._node_type_int = 5
        self.max_children = 1
        self.min_children = 1
        self._entry_class = OpaqueData
        super().__init__(tree_conf, data, page, next_page=next_page)

    def __repr__(self):
        return '<{}: page={} next_page={}>'.format(
            self.__class__.__name__, self.page, self.next_page
        )


class FreelistNode(Node):
    """
    Type 6: A phantom node representing a deallocated disk page.
    When a leaf or internal node is deleted, its page is marked as "Free" and added 
    to a linked list of available pages to prevent the database file from growing endlessly.
    """
    def __init__(self, tree_conf: TreeConf, data: Optional[bytes]=None,
                 page: int=None, next_page: int=None):
        self._node_type_int = 6
        self.max_children = 0
        self.min_children = 0
        super().__init__(tree_conf, data, page, next_page=next_page)

    def __repr__(self):
        return '<{}: page={} next_page={}>'.format(
            self.__class__.__name__, self.page, self.next_page
        )
