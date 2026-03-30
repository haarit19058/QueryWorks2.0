import json
import math
import os
import graphviz
from functools import partial
from logging import getLogger
from typing import Optional, Union, Iterator, Iterable

from . import utils
from .const import TreeConf
from .entry import Record, Reference, OpaqueData
from .memory import FileMemory
from .node import (
    Node, LonelyRootNode, RootNode, InternalNode, LeafNode, OverflowNode
)
from .serializer import Serializer, IntSerializer

logger = getLogger(__name__)

class BPlusTree:
    __slots__ = ['_filename', '_tree_conf', '_mem', '_root_node_page',
                 '_is_open', 'LonelyRootNode', 'RootNode', 'InternalNode',
                 'LeafNode', 'OverflowNode', 'Record', 'Reference']

    def __init__(self, filename: str, order: int=3, page_size: int=4096,
                 key_size: int=8, value_size: int=128, cache_size: int=64,
                 serializer: Optional[Serializer]=None):
        self._filename = filename
        self._tree_conf = TreeConf(
            page_size, order, key_size, value_size,
            serializer or IntSerializer()
        )
        self._create_partials()
        self._mem = FileMemory(filename, self._tree_conf, cache_size=cache_size)
        try:
            metadata = self._mem.get_metadata()
        except ValueError:
            self._initialize_empty_tree()
        else:
            self._root_node_page, self._tree_conf = metadata
        self._is_open = True

    def close(self):
        with self._mem.write_transaction:
            if not self._is_open:
                return
            self._mem.close()
            self._is_open = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ==========================================
    # YOUR CUSTOM API - MAPPED TO ACID BACKEND
    # ==========================================

    def search(self, key):
        """Search for a key, returning the deserialized value."""
        with self._mem.read_transaction:
            node = self._search_in_tree(key, self._root_node)
            try:
                record = node.get_entry(key)
                raw_bytes = self._get_value_from_record(record)
                return json.loads(raw_bytes.decode('utf-8'))
            except ValueError:
                return None

    def insert(self, key, value):
        """Insert key-value pair, routing through the ACID write transaction."""
        # Serialize your arbitrary Python objects to bytes for the database
        val_bytes = json.dumps(value).encode('utf-8')
        
        with self._mem.write_transaction:
            node = self._search_in_tree(key, self._root_node)
            try:
                existing_record = node.get_entry(key)
                # If it exists, update it (handling overflow pages if needed)
                if existing_record.overflow_page:
                    self._delete_overflow(existing_record.overflow_page)
                if len(val_bytes) <= self._tree_conf.value_size:
                    existing_record.value = val_bytes
                    existing_record.overflow_page = None
                else:
                    existing_record.value = None
                    existing_record.overflow_page = self._create_overflow(val_bytes)
                self._mem.set_node(node)
                return
            except ValueError:
                pass # Key doesn't exist, proceed with normal insert

            if len(val_bytes) <= self._tree_conf.value_size:
                record = self.Record(key, value=val_bytes)
            else:
                first_overflow_page = self._create_overflow(val_bytes)
                record = self.Record(key, value=None, overflow_page=first_overflow_page)

            if node.can_add_entry:
                node.insert_entry(record)
                self._mem.set_node(node)
            else:
                node.insert_entry(record)
                self._split_leaf(node)

    def update(self, key, new_value):
        """Update existing value. Returns True if successful."""
        # In this implementation, insert handles replacement implicitly
        val = self.search(key)
        if val is not None:
            self.insert(key, new_value)
            return True
        return False

    def range_query(self, start_key, end_key):
        """Efficient range query utilizing the B+Tree leaf sequence."""
        results = []
        
        # Simulate inclusive upper bound. 
        # If it's a string, append a null byte. If it's an int, add 1.
        if isinstance(end_key, str):
            stop_bound = end_key + '\x00'
        else:
            stop_bound = end_key + 1
            
        with self._mem.read_transaction:
            for record in self._iter_slice(slice(start_key, stop_bound)):
                if record.key > end_key:
                    break
                if record.key >= start_key:
                    raw_bytes = self._get_value_from_record(record)
                    results.append((record.key, json.loads(raw_bytes.decode('utf-8'))))
        return results

    def get_all(self):
        """Return all key-value pairs."""
        results = []
        with self._mem.read_transaction:
            for record in self._iter_slice(slice(None)):
                raw_bytes = self._get_value_from_record(record)
                results.append((record.key, json.loads(raw_bytes.decode('utf-8'))))
        return results

    def delete(self, key):
        """
        Delete key from tree safely within a transaction.
        Note: Persistent page-based B+Trees often defer complex structural 
        merges (underflow) to background vacuums to avoid locking. This method
        removes the record and cleans up the leaf space.
        """
        with self._mem.write_transaction:
            node = self._search_in_tree(key, self._root_node)
            try:
                record = node.get_entry(key)
                if record.overflow_page:
                    self._delete_overflow(record.overflow_page)
                node.remove_entry(key)
                self._mem.set_node(node)
                return True
            except ValueError:
                return False

    def visualize_tree(self, filename="bplustree_visualization"):
        """Generate Graphviz visualization adapted for persistent pages."""
        dot = graphviz.Digraph(name="B+Tree", format="png")
        dot.attr(rankdir="TB")
        dot.attr(nodesep="0.15", ranksep="0.5")
        dot.attr(size="22,16", ratio="compress")
        dot.node_attr.update(fontsize="8", fontname="Helvetica", margin="0.06,0.04")
        dot.edge_attr.update(arrowsize="0.5")

        with self._mem.read_transaction:
            if self._root_node:
                self._add_nodes(dot, self._root_node)
                self._add_edges(dot, self._root_node)

        os.makedirs("bplustree_images", exist_ok=True)
        if not filename.startswith("bplustree_images"):
            filename = os.path.join("bplustree_images", filename)

        dot.render(filename, cleanup=True)
        return dot

    def _add_nodes(self, dot, node):
        """Graphviz node creation mapped to persistent entries."""
        node_id = str(node.page)
        
        if isinstance(node, (LonelyRootNode, LeafNode)):
            items = []
            for entry in node.entries:
                k_str = str(entry.key)[:9] + ".." if len(str(entry.key)) > 11 else str(entry.key)
                
                raw_bytes = self._get_value_from_record(entry)
                val_obj = json.loads(raw_bytes.decode('utf-8'))
                
                if isinstance(val_obj, dict):
                    vals = list(val_obj.values())
                    v_str = str(vals[1]) if len(vals) > 1 else str(vals[0])
                else:
                    v_str = str(val_obj)
                    
                if len(v_str) > 10:
                    v_str = v_str[:9] + ".."
                    
                items.append(f"{k_str}:{v_str}")
                
            if len(items) > 4:
                items = items[:3] + [f"…+{len(items)-3}"]
                
            label = "\\n".join(items) if items else "Empty"
            dot.node(node_id, label, shape="box", style="filled", fillcolor="lightgreen")
            
        else:
            label = " | ".join(str(entry.key) for entry in node.entries)
            dot.node(node_id, label, shape="box", style="filled", fillcolor="lightblue")
            
            for entry in node.entries:
                child_node = self._mem.get_node(entry.after)
                self._add_nodes(dot, child_node)
            # Handle the 'before' pointer of the first entry
            if node.entries:
                first_child = self._mem.get_node(node.entries[0].before)
                self._add_nodes(dot, first_child)

    def _add_edges(self, dot, node):
        """Graphviz edge creation mapped to persistent page pointers."""
        node_id = str(node.page)
        
        if isinstance(node, InternalNode) or (isinstance(node, RootNode) and not isinstance(node, LonelyRootNode)):
            # Link to the 'before' page of the first entry
            if node.entries:
                dot.edge(node_id, str(node.entries[0].before))
            # Link to all 'after' pages
            for entry in node.entries:
                dot.edge(node_id, str(entry.after))
                child_node = self._mem.get_node(entry.after)
                self._add_edges(dot, child_node)
            if node.entries:
                first_child = self._mem.get_node(node.entries[0].before)
                self._add_edges(dot, first_child)
                
        elif isinstance(node, (LonelyRootNode, LeafNode)):
            if node.next_page:
                dot.edge(node_id, str(node.next_page), style="dashed", color="gray", constraint="false")

    # ==========================================
    # ACID INTERNAL IMPLEMENTATIONS 
    # ==========================================

    def _initialize_empty_tree(self):
        self._root_node_page = self._mem.next_available_page
        with self._mem.write_transaction:
            self._mem.set_node(self.LonelyRootNode(page=self._root_node_page))
        self._mem.set_metadata(self._root_node_page, self._tree_conf)

    def _create_partials(self):
        self.LonelyRootNode = partial(LonelyRootNode, self._tree_conf)
        self.RootNode = partial(RootNode, self._tree_conf)
        self.InternalNode = partial(InternalNode, self._tree_conf)
        self.LeafNode = partial(LeafNode, self._tree_conf)
        self.OverflowNode = partial(OverflowNode, self._tree_conf)
        self.Record = partial(Record, self._tree_conf)
        self.Reference = partial(Reference, self._tree_conf)

    @property
    def _root_node(self) -> Union['LonelyRootNode', 'RootNode']:
        root_node = self._mem.get_node(self._root_node_page)
        return root_node

    @property
    def _left_record_node(self) -> Union['LonelyRootNode', 'LeafNode']:
        node = self._root_node
        while not isinstance(node, (LonelyRootNode, LeafNode)):
            node = self._mem.get_node(node.smallest_entry.before)
        return node

    def _iter_slice(self, slice_: slice) -> Iterator[Record]:
        if slice_.start is None:
            node = self._left_record_node
        else:
            node = self._search_in_tree(slice_.start, self._root_node)

        while True:
            for entry in node.entries:
                if slice_.start is not None and entry.key < slice_.start:
                    continue
                if slice_.stop is not None and entry.key >= slice_.stop:
                    return
                yield entry
            if node.next_page:
                node = self._mem.get_node(node.next_page)
            else:
                return

    def _search_in_tree(self, key, node) -> 'Node':
        if isinstance(node, (LonelyRootNode, LeafNode)):
            return node
        page = None
        if key < node.smallest_key:
            page = node.smallest_entry.before
        elif node.biggest_key <= key:
            page = node.biggest_entry.after
        else:
            for ref_a, ref_b in utils.pairwise(node.entries):
                if ref_a.key <= key < ref_b.key:
                    page = ref_a.after
                    break
        child_node = self._mem.get_node(page)
        child_node.parent = node
        return self._search_in_tree(key, child_node)

    def _split_leaf(self, old_node: 'Node'):
        parent = old_node.parent
        new_node = self.LeafNode(page=self._mem.next_available_page, next_page=old_node.next_page)
        new_entries = old_node.split_entries()
        new_node.entries = new_entries
        ref = self.Reference(new_node.smallest_key, old_node.page, new_node.page)

        if isinstance(old_node, LonelyRootNode):
            old_node = old_node.convert_to_leaf()
            self._create_new_root(ref)
        elif parent.can_add_entry:
            parent.insert_entry(ref)
            self._mem.set_node(parent)
        else:
            parent.insert_entry(ref)
            self._split_parent(parent)

        old_node.next_page = new_node.page
        self._mem.set_node(old_node)
        self._mem.set_node(new_node)

    def _split_parent(self, old_node: Node):
        parent = old_node.parent
        new_node = self.InternalNode(page=self._mem.next_available_page)
        new_entries = old_node.split_entries()
        new_node.entries = new_entries

        ref = new_node.pop_smallest()
        ref.before = old_node.page
        ref.after = new_node.page

        if isinstance(old_node, RootNode):
            old_node = old_node.convert_to_internal()
            self._create_new_root(ref)
        elif parent.can_add_entry:
            parent.insert_entry(ref)
            self._mem.set_node(parent)
        else:
            parent.insert_entry(ref)
            self._split_parent(parent)

        self._mem.set_node(old_node)
        self._mem.set_node(new_node)

    def _create_new_root(self, reference: Reference):
        new_root = self.RootNode(page=self._mem.next_available_page)
        new_root.insert_entry(reference)
        self._root_node_page = new_root.page
        self._mem.set_metadata(self._root_node_page, self._tree_conf)
        self._mem.set_node(new_root)

    def _create_overflow(self, value: bytes) -> int:
        first_overflow_page = self._mem.next_available_page
        next_overflow_page = first_overflow_page

        iterator = utils.iter_slice(value, self.OverflowNode().max_payload)
        for slice_value, is_last in iterator:
            current_overflow_page = next_overflow_page
            next_overflow_page = None if is_last else self._mem.next_available_page

            overflow_node = self.OverflowNode(page=current_overflow_page, next_page=next_overflow_page)
            overflow_node.insert_entry_at_the_end(OpaqueData(data=slice_value))
            self._mem.set_node(overflow_node)

        return first_overflow_page

    def _traverse_overflow(self, first_overflow_page: int):
        next_overflow_page = first_overflow_page
        while True:
            overflow_node = self._mem.get_node(next_overflow_page)
            yield overflow_node
            next_overflow_page = overflow_node.next_page
            if next_overflow_page is None:
                break

    def _read_from_overflow(self, first_overflow_page: int) -> bytes:
        rv = bytearray()
        for overflow_node in self._traverse_overflow(first_overflow_page):
            rv.extend(overflow_node.smallest_entry.data)
        return bytes(rv)

    def _delete_overflow(self, first_overflow_page: int):
        for overflow_node in self._traverse_overflow(first_overflow_page):
            self._mem.del_node(overflow_node)

    def _get_value_from_record(self, record: Record) -> bytes:
        if record.value is not None:
            return record.value
        return self._read_from_overflow(record.overflow_page)
