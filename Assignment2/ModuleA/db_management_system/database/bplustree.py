"""
B+ Tree Implementation

Supports:
- Insert (with splitting)
- Delete (with merge/borrow)
- Search (binary search in leaves)
- Range Query (via linked leaves)

Leaf nodes are connected as a doubly linked list for efficient range queries.
"""

import math
import graphviz
import os


class Node:
    """
    Base node class for B+ Tree
    """
    
    def __init__(self, order):
        self.order = order
        self.keys = []
        self.parent = None

    def is_full(self):
        return len(self.keys) == self.order


class LeafNode(Node):
    """
    Leaf nodes store actual key-value pairs and are linked (DLL)
    """

    def __init__(self, order):
        super().__init__(order)
        self.prev = None
        self.next = None
        self.values = []


class InternalNode(Node):
    """
    Internal nodes store keys and child pointers
    """
    
    def __init__(self, order):
        super().__init__(order)
        self.children = []


class BPlusTree:

    def __init__(self, order=3, dtype=int):
        self.root = LeafNode(order)
        self.order = order
        self.dtype = dtype


    def search(self, key):
        """
        Search for a key in the B+ Tree.

        Steps:
        1. Navigate to correct leaf using _find_leaf
        2. Perform binary search within leaf node

        Returns:
            value if found, else None
        """
        leaf = self._find_leaf(key)
        start = 0
        end = len(leaf.keys) - 1

        while start <= end:
            mid = (start + end) // 2

            if key > leaf.keys[mid]:
                start = mid + 1

            elif key == leaf.keys[mid]:
                return leaf.values[mid]

            else:
                end = mid - 1

        return None


    def _find_leaf(self, key):
        """
        Traverse from root to find the correct leaf node for a key.
        """
        curr = self.root

        while isinstance(curr, InternalNode):
            i = 0

            while i < len(curr.keys) and key >= curr.keys[i]:
                i += 1

            curr = curr.children[i]

        return curr


    def insert(self, key, value):
        """
        Insert key-value pair into tree.
        Handles root split if root becomes full.
        """
        root = self.root

        if len(root.keys) == self.order - 1:
            new_root = InternalNode(self.order)
            new_root.children.append(self.root)
            self.root = new_root

            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, value)

        else:
            self._insert_non_full(root, key, value)


    def _insert_non_full(self, node, key, value):
        """
        Insert into a node guaranteed to be non-full.
        Performs recursive insertion and splits children if needed.
        """
        if isinstance(node, LeafNode):
            insert_idx = 0

            while insert_idx < len(node.keys) and key > node.keys[insert_idx]:
                insert_idx += 1
                
            # handle duplicate key — update value instead of inserting twice
            if insert_idx < len(node.keys) and node.keys[insert_idx] == key:
                node.values[insert_idx] = value
                return

            node.keys.insert(insert_idx, key)
            node.values.insert(insert_idx, value)

        else:
            insert_idx = 0

            while insert_idx < len(node.keys) and key >= node.keys[insert_idx]:
                insert_idx += 1

            child = node.children[insert_idx]

            if len(child.keys) == self.order - 1:
                self._split_child(node, insert_idx)

                if key >= node.keys[insert_idx]:
                    insert_idx += 1

            self._insert_non_full(node.children[insert_idx], key, value)


    def _split_child(self, parent, index):
        """
        Split a full child node.

        Leaf:
        - Split keys & values
        - Maintain linked list

        Internal:
        - Promote middle key
        - Split children
        """
        child = parent.children[index]
        mid = len(child.keys) // 2
        promoted_key = child.keys[mid]

        if isinstance(child, LeafNode):
            new_child = LeafNode(self.order)

            new_child.keys = child.keys[mid:]
            new_child.values = child.values[mid:]

            child.keys = child.keys[:mid]
            child.values = child.values[:mid]

            new_child.next = child.next

            if child.next:
                child.next.prev = new_child

            child.next = new_child
            new_child.prev = child

        else:
            new_child = InternalNode(self.order)

            new_child.keys = child.keys[mid + 1:]
            new_child.children = child.children[mid + 1:]

            child.keys = child.keys[:mid]
            child.children = child.children[:mid + 1]

        parent.keys.insert(index, promoted_key)
        parent.children.insert(index + 1, new_child)
      
        
    def update(self, key, new_value):
        """
        Update value associated with an existing key.
        Return True if successful.
        """
        leaf = self._find_leaf(key)

        for i, k in enumerate(leaf.keys):

            if k == key:
                leaf.values[i] = new_value

                return True

        return False


    def range_query(self, start_key, end_key):
        """
        Efficient range query using linked leaf nodes.
        Traverses sequentially from start_key to end_key.
        """
        leaf = self._find_leaf(start_key)
        results = []

        while leaf:

            for i, key in enumerate(leaf.keys):

                if key > end_key:
                    return results

                if key >= start_key:
                    results.append((key, leaf.values[i]))

            leaf = leaf.next

        return results


    def get_all(self):
        """
        Return all key-value pairs in sorted order.

        Process:
        - Go to leftmost leaf
        - Traverse using next pointers
        """
        results = []
        node = self.root

        while isinstance(node, InternalNode):
            node = node.children[0]

        while node:

            for i in range(len(node.keys)):
                results.append((node.keys[i], node.values[i]))

            node = node.next

        return results


    def _fmt_key(self, key):
        """
        Shorten a key for display. Truncates long strings such as UUIDs.
        """
        s = str(key)
        return s[:9] + ".." if len(s) > 11 else s


    def visualize_tree(self, filename="bplustree_visualization"):
        """
        Generate Graphviz visualization of B+ Tree.
        
        Shows:
        - Node hierarchy
        - Parent-child edges
        - Leaf node linkage (dashed)
        """
        dot = graphviz.Digraph(name="B+Tree", format="png")
        dot.attr(rankdir="TB")
        dot.attr(nodesep="0.15", ranksep="0.5")
        dot.attr(size="22,16", ratio="compress")
        dot.node_attr.update(fontsize="8", fontname="Helvetica", margin="0.06,0.04")
        dot.edge_attr.update(arrowsize="0.5")

        if self.root:
            self._add_nodes(dot, self.root)
            self._add_edges(dot, self.root)

        # create folder if not exists
        os.makedirs("bplustree_images", exist_ok=True)

        # prepend folder path
        if not filename.startswith("bplustree_images"):
            filename = os.path.join("bplustree_images", filename)

        dot.render(filename, cleanup=True)
        return dot


    def _add_nodes(self, dot, node):
        """
        Recursively add nodes to Graphviz structure.

        Leaf - Show key:value pairs
        Internal - Show only keys
        """
        if isinstance(node, LeafNode):
            items = []
            
            for i in range(len(node.keys)):
                k_str = self._fmt_key(node.keys[i])
                v_str = str(node.values[i])
                
                # For dict values show only the first meaningful field
                if isinstance(node.values[i], dict):
                    vals = list(node.values[i].values())
                    v_str = str(vals[1]) if len(vals) > 1 else str(vals[0])
                
                if len(v_str) > 10:
                    v_str = v_str[:9] + ".."
                
                items.append(f"{k_str}:{v_str}")
            
            # Cap display at 4 entries to prevent nodes becoming too tall
            if len(items) > 4:
                items = items[:3] + [f"…+{len(items)-3}"]
            
            label = "\\n".join(items)
            dot.node(
                str(id(node)), label,
                shape="box", style="filled", fillcolor="lightgreen"
            )
        
        else:
            label = " | ".join(self._fmt_key(k) for k in node.keys)
            dot.node(
                str(id(node)), label,
                shape="box", style="filled", fillcolor="lightblue"
            )
            
            for child in node.children:
                self._add_nodes(dot, child)


    def _add_edges(self, dot, node):
        """
        Add edges between nodes.

        Internal - Parent → child edges
        Leaf - Dashed edges to represent linked list
        """
        if isinstance(node, InternalNode):

            for child in node.children:
                dot.edge(str(id(node)), str(id(child)))
                self._add_edges(dot, child)

        elif isinstance(node, LeafNode):

            if node.next:
                dot.edge(
                    str(id(node)),
                    str(id(node.next)),
                    style="dashed",
                    color="gray",
                    constraint="false"
                )
       
                
    def delete(self, key):
        """
        Delete key from tree.
        
        Handles underflow using:
        - Borrow from siblings
        - Merge nodes
        """
        if not self.root:
            return False

        deleted = self._delete(self.root, key)

        if isinstance(self.root, InternalNode) and len(self.root.keys) == 0:
            self.root = self.root.children[0]

        return deleted


    def _delete(self, node, key):
        """
        Recursive deletion helper.

        Leaf:
        - Directly remove key-value pair

        Internal:
        - Traverse to correct child
        - After deletion, check for underflow
        - Fix using borrow or merge
        """
        if isinstance(node, LeafNode):

            for i, k in enumerate(node.keys):

                if k == key:
                    node.keys.pop(i)
                    node.values.pop(i)

                    return True

            return False

        else:
            i = 0

            while i < len(node.keys) and key >= node.keys[i]:
                i += 1

            deleted = self._delete(node.children[i], key)
            min_keys = math.ceil(self.order / 2) - 1

            if len(node.children[i].keys) < min_keys:
                self._fill_child(node, i)

            return deleted


    def _fill_child(self, node, index):
        """
        Fix underflow in child node.

        Strategy:
        1. Try borrowing from left sibling
        2. Else try borrowing from right sibling
        3. Else merge with sibling
        """
        min_keys = math.ceil(self.order / 2) - 1

        if index > 0 and len(node.children[index - 1].keys) > min_keys:
            self._borrow_from_prev(node, index)

        elif index < len(node.children) - 1 and len(node.children[index + 1].keys) > min_keys:
            self._borrow_from_next(node, index)

        else:
            if index < len(node.children) - 1:
                self._merge(node, index)

            else:
                self._merge(node, index - 1)


    def _borrow_from_prev(self, node, index):
        """
        Borrow a key from left sibling.

        Leaf:
        - Move last key from sibling to front of child

        Internal:
        - Move parent key down
        - Move sibling key up
        """
        child = node.children[index]
        sibling = node.children[index - 1]

        if isinstance(child, LeafNode):
            child.keys.insert(0, sibling.keys.pop())
            child.values.insert(0, sibling.values.pop())

            node.keys[index - 1] = child.keys[0]

        else:
            child.keys.insert(0, node.keys[index - 1])
            child.children.insert(0, sibling.children.pop())

            node.keys[index - 1] = sibling.keys.pop()


    def _borrow_from_next(self, node, index):
        """
        Borrow a key from right sibling.

        Leaf:
        - Move first key from sibling to end of child

        Internal:
        - Move parent key down
        - Replace with sibling key
        """
        child = node.children[index]
        sibling = node.children[index + 1]

        if isinstance(child, LeafNode):
            child.keys.append(sibling.keys.pop(0))
            child.values.append(sibling.values.pop(0))

            node.keys[index] = sibling.keys[0]

        else:
            child.keys.append(node.keys[index])
            child.children.append(sibling.children.pop(0))

            node.keys[index] = sibling.keys.pop(0)


    def _merge(self, node, index):
        """
        Merge child at index with its right sibling.

        Leaf:
        - Combine keys and values
        - Fix linked list pointers

        Internal:
        - Pull parent key down
        - Merge children

        Also removes key from parent.
        """
        left_child = node.children[index]
        right_child = node.children[index + 1]

        if isinstance(left_child, LeafNode):
            left_child.keys.extend(right_child.keys)
            left_child.values.extend(right_child.values)
            left_child.next = right_child.next

            if right_child.next:
                right_child.next.prev = left_child

        else:
            left_child.keys.append(node.keys[index])
            left_child.keys.extend(right_child.keys)
            left_child.children.extend(right_child.children)

        node.keys.pop(index)
        node.children.pop(index + 1)