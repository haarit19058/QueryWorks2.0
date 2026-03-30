"""
Disk-level Entry representations for the B+ Tree.

This module defines how individual pieces of data (keys, values, and page pointers) 
are structurally packed into fixed-length byte arrays to be written to disk pages.
It heavily utilizes "Lazy Loading" to avoid deserializing bytes into Python objects 
unless absolutely necessary, saving significant CPU and RAM.
"""
import abc
from typing import Optional

from .const import (ENDIAN, PAGE_REFERENCE_BYTES,
                    USED_KEY_LENGTH_BYTES, USED_VALUE_LENGTH_BYTES, TreeConf)


# A singleton marker used to indicate that a specific attribute (like a key or value)
# is still in its raw binary form and hasn't been parsed into a Python object yet.
NOT_LOADED = object()


class Entry(metaclass=abc.ABCMeta):
    """Abstract base definition for any entity that lives inside a B+ Tree node."""

    __slots__ = []

    @abc.abstractmethod
    def load(self, data: bytes):
        """Parse raw binary data from the disk into this object's attributes."""

    @abc.abstractmethod
    def dump(self) -> bytes:
        """Pack this object's attributes into a raw, fixed-length binary string."""


class ComparableEntry(Entry, metaclass=abc.ABCMeta):
    """
    An Entry that supports rich comparison operators. 
    This allows Python's `bisect` module to perform rapid binary searches 
    through a list of these entries based solely on their `key` attribute.
    """

    __slots__ = []

    def __eq__(self, other):
        return self.key == other.key

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key

    def __gt__(self, other):
        return self.key > other.key

    def __ge__(self, other):
        return self.key >= other.key


class Record(ComparableEntry):
    """
    Represents a standard Key-Value pair stored in a Leaf Node.
    
    To ensure we can instantly calculate the position of any record on a disk page,
    every Record occupies an identical, fixed number of bytes, padding shorter keys 
    and values with null bytes.
    """

    __slots__ = ['_tree_conf', 'length', '_key', '_value', '_overflow_page',
                 '_data']

    def __init__(self, tree_conf: TreeConf, key=None,
                 value: Optional[bytes]=None, data: Optional[bytes]=None,
                 overflow_page: Optional[int]=None):
        self._tree_conf = tree_conf
        
        # Calculate the absolute fixed width this record will consume on disk
        self.length = (
            USED_KEY_LENGTH_BYTES + self._tree_conf.key_size +
            USED_VALUE_LENGTH_BYTES + self._tree_conf.value_size +
            PAGE_REFERENCE_BYTES
        )
        self._data = data

        if self._data:
            # If instantiated from disk bytes, defer parsing until properties are accessed
            self._key = NOT_LOADED
            self._value = NOT_LOADED
            self._overflow_page = NOT_LOADED
        else:
            # If instantiated in memory (e.g., during an insert operation)
            self._key = key
            self._value = value
            self._overflow_page = overflow_page

    @property
    def key(self):
        if self._key is NOT_LOADED:
            self.load(self._data)
        return self._key

    @key.setter
    def key(self, val):
        self._data = None
        self._key = val

    @property
    def value(self):
        if self._value is NOT_LOADED:
            self.load(self._data)
        return self._value

    @value.setter
    def value(self, val):
        self._data = None
        self._value = val

    @property
    def overflow_page(self):
        if self._overflow_page is NOT_LOADED:
            self.load(self._data)
        return self._overflow_page

    @overflow_page.setter
    def overflow_page(self, val):
        self._data = None
        self._overflow_page = val

    def load(self, data: bytes):
        """Extracts the exact key, value, and overflow metadata from padded bytes."""
        assert len(data) == self.length, "Data chunk size does not match expected Record length"

        # 1. Parse Key Length and Data
        idx_key_len = USED_KEY_LENGTH_BYTES
        actual_key_len = int.from_bytes(data[0:idx_key_len], ENDIAN)
        assert 0 <= actual_key_len <= self._tree_conf.key_size

        idx_key_end = idx_key_len + actual_key_len
        self._key = self._tree_conf.serializer.deserialize(
            data[idx_key_len:idx_key_end]
        )

        # 2. Parse Value Length and Data (skipping the null-byte padding of the key space)
        idx_val_len_start = idx_key_len + self._tree_conf.key_size
        idx_val_len_end = idx_val_len_start + USED_VALUE_LENGTH_BYTES
        
        actual_val_len = int.from_bytes(
            data[idx_val_len_start:idx_val_len_end], ENDIAN
        )
        assert 0 <= actual_val_len <= self._tree_conf.value_size

        idx_val_end = idx_val_len_end + actual_val_len

        # 3. Parse Overflow Page Pointer (located at the very end of the allocated block)
        idx_overflow_start = idx_val_len_end + self._tree_conf.key_size # Note: The original logic skipped forward based on max value size
        idx_overflow_start = idx_val_len_end + self._tree_conf.value_size 
        idx_overflow_end = idx_overflow_start + PAGE_REFERENCE_BYTES
        
        target_overflow_page = int.from_bytes(
            data[idx_overflow_start:idx_overflow_end], ENDIAN
        )

        if target_overflow_page:
            self._overflow_page = target_overflow_page
            self._value = None
        else:
            self._overflow_page = None
            self._value = data[idx_val_len_end:idx_val_end]

    def dump(self) -> bytes:
        """Packs the record into a fixed-width binary sequence, padding empty space with zeros."""
        if self._data:
            return self._data

        assert self._value is None or self._overflow_page is None, "Cannot have both a value and an overflow pointer"
        
        # Serialize the primary key
        serialized_key = self._tree_conf.serializer.serialize(
            self._key, self._tree_conf.key_size
        )
        active_key_len = len(serialized_key)
        
        # Handle the payload (either raw value or empty if overflowing)
        target_overflow = self._overflow_page or 0
        active_value = b'' if target_overflow else self._value
        active_val_len = len(active_value)

        # Construct the final binary layout
        packed_data = (
            active_key_len.to_bytes(USED_VALUE_LENGTH_BYTES, ENDIAN) +
            serialized_key +
            bytes(self._tree_conf.key_size - active_key_len) +  # Key Padding
            active_val_len.to_bytes(USED_VALUE_LENGTH_BYTES, ENDIAN) +
            active_value +
            bytes(self._tree_conf.value_size - active_val_len) + # Value Padding
            target_overflow.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN)
        )
        return packed_data

    def __repr__(self):
        if self.overflow_page:
            return '<Record: {} (Overflowing Payload)>'.format(self.key)
        if self.value:
            return '<Record: {} payload={}>'.format(self.key, self.value[0:16])
        return '<Record: {} (Unknown State)>'.format(self.key)


class Reference(ComparableEntry):
    """
    Represents a routing pointer inside an Internal or Root Node.
    It contains a 'split key' and two pointers: 'before' and 'after', dictating
    which child page to load based on where a search key falls.
    """

    __slots__ = ['_tree_conf', 'length', '_key', '_before', '_after', '_data']

    def __init__(self, tree_conf: TreeConf, key=None, before=None, after=None,
                 data: bytes=None):
        self._tree_conf = tree_conf
        
        # Calculate fixed width: 2 page pointers + 1 key length indicator + max key size
        self.length = (
            2 * PAGE_REFERENCE_BYTES +
            USED_KEY_LENGTH_BYTES +
            self._tree_conf.key_size
        )
        self._data = data

        if self._data:
            self._key = NOT_LOADED
            self._before = NOT_LOADED
            self._after = NOT_LOADED
        else:
            self._key = key
            self._before = before
            self._after = after

    @property
    def key(self):
        if self._key is NOT_LOADED:
            self.load(self._data)
        return self._key

    @key.setter
    def key(self, val):
        self._data = None
        self._key = val

    @property
    def before(self):
        if self._before is NOT_LOADED:
            self.load(self._data)
        return self._before

    @before.setter
    def before(self, val):
        self._data = None
        self._before = val

    @property
    def after(self):
        if self._after is NOT_LOADED:
            self.load(self._data)
        return self._after

    @after.setter
    def after(self, val):
        self._data = None
        self._after = val

    def load(self, data: bytes):
        """Unpacks the routing pointers and split key from disk bytes."""
        assert len(data) == self.length
        
        # 1. Left child page pointer
        idx_before_end = PAGE_REFERENCE_BYTES
        self._before = int.from_bytes(data[0:idx_before_end], ENDIAN)

        # 2. Active key length and serialized key
        idx_key_len_end = idx_before_end + USED_KEY_LENGTH_BYTES
        active_key_len = int.from_bytes(
            data[idx_before_end:idx_key_len_end], ENDIAN
        )
        assert 0 <= active_key_len <= self._tree_conf.key_size

        idx_key_end = idx_key_len_end + active_key_len
        self._key = self._tree_conf.serializer.deserialize(
            data[idx_key_len_end:idx_key_end]
        )

        # 3. Right child page pointer (skipping past key padding)
        idx_after_start = idx_key_len_end + self._tree_conf.key_size
        idx_after_end = idx_after_start + PAGE_REFERENCE_BYTES
        self._after = int.from_bytes(data[idx_after_start:idx_after_end], ENDIAN)

    def dump(self) -> bytes:
        """Packs the routing pointers and keys, ensuring fixed-length boundaries."""
        if self._data:
            return self._data

        assert isinstance(self._before, int)
        assert isinstance(self._after, int)

        serialized_key = self._tree_conf.serializer.serialize(
            self._key, self._tree_conf.key_size
        )
        active_key_len = len(serialized_key)

        packed_data = (
            self._before.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN) +
            active_key_len.to_bytes(USED_VALUE_LENGTH_BYTES, ENDIAN) +
            serialized_key +
            bytes(self._tree_conf.key_size - active_key_len) + # Key Padding
            self._after.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN)
        )
        return packed_data

    def __repr__(self):
        return '<Reference: key={} left_page={} right_page={}>'.format(
            self.key, self.before, self.after
        )


class OpaqueData(Entry):
    """
    A lightweight container for raw binary chunks that exceed the maximum 
    allowed value size. These are dumped directly into Overflow Nodes.
    """

    __slots__ = ['data']

    def __init__(self, tree_conf: TreeConf=None, data: bytes=None):
        self.data = data

    def load(self, data: bytes):
        self.data = data

    def dump(self) -> bytes:
        return self.data

    def __repr__(self):
        return '<OpaqueData Payload: {} bytes>'.format(len(self.data) if self.data else 0)
