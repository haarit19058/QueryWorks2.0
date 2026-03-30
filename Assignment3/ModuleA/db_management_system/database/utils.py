"""
Utility functions for iteration and byte manipulation.
These helpers support the B+ Tree's node traversal and payload chunking.
"""
import itertools
from typing import Iterable


def pairwise(iterable: Iterable):
    """
    Generates overlapping consecutive pairs from a given iterable.
    
    This is particularly useful when scanning through B+ Tree entry boundaries
    (e.g., iterating over reference nodes to see if a search key falls between 
    reference A and reference B).
    
    Example:
        Input: [A, B, C, D]
        Output: (A, B), (B, C), (C, D)
    """
    iter_first, iter_second = itertools.tee(iterable)
    
    # Advance the second iterator by one step to create the offset
    next(iter_second, None)
    
    return zip(iter_first, iter_second)


def iter_slice(iterable: bytes, n: int):
    """
    Chunks a byte sequence into fixed-size segments.
    
    It yields each chunk along with a boolean flag indicating if it is the 
    final segment. This is critical for the database to safely distribute 
    large data payloads across multiple chained overflow pages.
    
    Example:
        Input: (b'ABCDE', 2)
        Output: (b'AB', False), (b'CD', False), (b'E', True)
    """
    current_idx = 0
    next_idx = current_idx + n
    total_length = len(iterable)

    while True:
        # Terminate if we have consumed the entire byte sequence
        if current_idx >= total_length:
            break

        # Extract the chunk for the current window
        chunk = iterable[current_idx:next_idx]
        
        # Shift the indexing window forward for the next iteration
        current_idx = next_idx
        next_idx = current_idx + n
        
        # Check if shifting forward pushed us past the total length
        is_final_chunk = current_idx >= total_length
        
        yield chunk, is_final_chunk
