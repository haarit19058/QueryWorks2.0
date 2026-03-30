"""
Core configurations and byte-length constants for the B+ Tree storage engine.
These constants dictate the binary layout of pages and records on disk.
"""
from collections import namedtuple

# Database build version
VERSION = '0.0.4.dev1'

# System byte order for all binary integer serialization
ENDIAN = 'little'

# --- Memory & Addressing Configurations ---

# Allocates 4 bytes for page pointers. 
# Assuming a standard 4KB page size, this allows the database to address up to 16 TB of data.
PAGE_REFERENCE_BYTES = 4

# --- Page Header Definitions ---

# Allocates 1 byte to designate the node category (e.g., internal, leaf, overflow, freelist).
NODE_TYPE_BYTES = 1

# Allocates 3 bytes to track exactly how much of the page's capacity is currently holding active data.
USED_PAGE_LENGTH_BYTES = 3

# --- Record Payload Limits ---

# Allocates 2 bytes each for tracking the length of stored keys and values.
# This mathematically restricts the maximum size of any single key or value to 64 KB (2^16 bytes).
USED_KEY_LENGTH_BYTES = 2
USED_VALUE_LENGTH_BYTES = 2

# --- Write-Ahead Log (WAL) Configurations ---

# Allocates 1 byte for WAL frame categorization (supporting up to 256 unique frame operations).
FRAME_TYPE_BYTES = 1

# Standard 4-byte allocation for general-purpose metadata integers (like page size or order).
OTHERS_BYTES = 4


# --- Tree Configuration Container ---

# A lightweight container passed throughout the system to maintain tree parameters.
TreeConf = namedtuple('TreeConf', [
    'page_size',   # Total byte allocation per discrete page on disk
    'order',       # Maximum branching factor (children per node)
    'key_size',    # Upper bound limit for serialized key length in bytes
    'value_size',  # Upper bound limit for serialized value length in bytes
    'serializer',  # The dedicated serializer instance for encoding/decoding keys
])
