"""
Transactional Storage Engine and Memory Manager.

This module handles physical disk I/O, caching, and concurrency. 
It guarantees ACID properties by utilizing:
1. RWLocks for Isolation (Multiple Readers, Single Writer).
2. Write-Ahead Logging (WAL) for Atomicity (Rollbacks) and Durability (Crash Recovery).
3. File Fsyncs to ensure data is physically written to the hardware platter.
"""
import enum
import io
from logging import getLogger
import os
import platform
from typing import Union, Tuple, Optional

import cachetools
import rwlock

from .node import Node, FreelistNode
from .const import (
    ENDIAN, PAGE_REFERENCE_BYTES, OTHERS_BYTES, TreeConf, FRAME_TYPE_BYTES
)

logger = getLogger(__name__)


class ReachedEndOfFile(Exception):
    """Raised when the file stream hits the physical end of the disk file."""


# ==============================================================================
# LOW-LEVEL HARDWARE I/O HELPERS
# ==============================================================================

def open_file_in_dir(path: str) -> Tuple[io.FileIO, Optional[int]]:
    """
    Safely opens a database file and its parent directory.
    
    Opening the directory is required on Unix systems to properly fsync 
    file metadata (like file size changes) to disk, preventing corruption 
    during power loss.
    """
    target_dir = os.path.dirname(path)
    if not os.path.isdir(target_dir):
        raise ValueError('Target directory does not exist: {}'.format(target_dir))

    # Open exclusively to create if missing, otherwise open for read/write binary
    if not os.path.exists(path):
        db_stream = open(path, mode='x+b', buffering=0)
    else:
        db_stream = open(path, mode='r+b', buffering=0)

    # Windows handles directory persistence differently, so we bypass directory syncing there
    if platform.system() == 'Windows':
        dir_descriptor = None
    else:
        dir_descriptor = os.open(target_dir, os.O_RDONLY)

    return db_stream, dir_descriptor


def write_to_file(db_stream: io.FileIO, dir_descriptor: Optional[int],
                  byte_chunk: bytes, fsync: bool=True):
    """Writes a chunk of bytes to the stream, ensuring the entire payload is committed."""
    target_length = len(byte_chunk)
    bytes_written = 0
    
    while bytes_written < target_length:
        bytes_written += db_stream.write(byte_chunk[bytes_written:])
        
    if fsync:
        fsync_file_and_dir(db_stream.fileno(), dir_descriptor)


def fsync_file_and_dir(file_descriptor: int, dir_descriptor: Optional[int]):
    """Forces the OS to flush buffers and physically write data to the hardware."""
    os.fsync(file_descriptor)
    if dir_descriptor is not None:
        os.fsync(dir_descriptor)


def read_from_file(db_stream: io.FileIO, start_byte: int, stop_byte: int) -> bytes:
    """Reads a precise byte range from the disk file."""
    chunk_size = stop_byte - start_byte
    assert chunk_size >= 0
    
    db_stream.seek(start_byte)
    read_buffer = bytes()
    
    while db_stream.tell() < stop_byte:
        fetched_data = db_stream.read(stop_byte - db_stream.tell())
        if fetched_data == b'':
            raise ReachedEndOfFile('Unexpected end of file reached during read.')
        read_buffer += fetched_data
        
    assert len(read_buffer) == chunk_size
    return read_buffer


class FakeCache:
    """A dummy cache that acts as a passthrough when cache size is set to 0."""
    def get(self, k): pass
    def __setitem__(self, key, value): pass
    def clear(self): pass


# ==============================================================================
# MAIN TRANSACTIONAL MEMORY MANAGER
# ==============================================================================

class FileMemory:
    """
    Orchestrates memory access for the B+ Tree.
    Translates abstract Page IDs into physical disk reads/writes, manages 
    the LRU cache to minimize disk hits, and provides transactional boundaries.
    """

    __slots__ = ['_filename', '_tree_conf', '_lock', '_cache', '_fd',
                 '_dir_fd', '_wal', 'last_page', '_freelist_start_page',
                 '_root_node_page']

    def __init__(self, filename: str, tree_conf: TreeConf, cache_size: int=512):
        self._filename = filename
        self._tree_conf = tree_conf
        
        # Enforces the 1-Writer, N-Readers concurrency model
        self._lock = rwlock.RWLock()

        if cache_size == 0:
            self._cache = FakeCache()
        else:
            self._cache = cachetools.LRUCache(maxsize=cache_size)

        self._fd, self._dir_fd = open_file_in_dir(filename)

        # Initialize the Write-Ahead Log to catch inflight transactions
        self._wal = WAL(filename, tree_conf.page_size)
        if self._wal.needs_recovery:
            # If the database crashed previously, flush the WAL to recover state
            self.perform_checkpoint(reopen_wal=True)

        # Determine the physical bounds of the file to track available page IDs
        self._fd.seek(0, io.SEEK_END)
        end_of_file_byte = self._fd.tell()
        self.last_page = int(end_of_file_byte / self._tree_conf.page_size)
        self._freelist_start_page = 0
        self._root_node_page = 0

    def get_node(self, page: int):
        """
        Retrieves a Node. 
        Checks the RAM cache first, then the WAL (uncommitted writes), and finally the main disk.
        """
        cached_node = self._cache.get(page)
        if cached_node is not None:
            return cached_node

        raw_page_data = self._wal.get_page(page)
        if not raw_page_data:
            raw_page_data = self._read_page(page)

        parsed_node = Node.from_page_data(self._tree_conf, data=raw_page_data, page=page)
        self._cache[parsed_node.page] = parsed_node
        return parsed_node

    def set_node(self, node: Node):
        """Stages a node for writing by sending it to the WAL and updating the RAM cache."""
        self._wal.set_page(node.page, node.dump())
        self._cache[node.page] = node

    def del_node(self, node: Node):
        self._insert_in_freelist(node.page)

    def del_page(self, page: int):
        self._insert_in_freelist(page)

    @property
    def read_transaction(self):
        """Context manager that acquires a shared read lock."""
        class ReadTransaction:
            def __enter__(self2):
                self._lock.reader_lock.acquire()
            def __exit__(self2, exc_type, exc_val, exc_tb):
                self._lock.reader_lock.release()
        return ReadTransaction()

    @property
    def write_transaction(self):
        """Context manager that acquires an exclusive write lock and enforces Atomicity."""
        class WriteTransaction:
            def __enter__(self2):
                self._lock.writer_lock.acquire()

            def __exit__(self2, exc_type, exc_val, exc_tb):
                if exc_type:
                    # ATOMICITY: If an exception occurred during the transaction, discard all changes
                    self._wal.rollback()
                    self._cache.clear()
                else:
                    # ATOMICITY: If successful, commit all changes simultaneously
                    self._wal.commit()
                self._lock.writer_lock.release()
        return WriteTransaction()

    @property
    def next_available_page(self) -> int:
        """Finds an empty page space. Recycles a freed page if available, otherwise expands the file."""
        recycled_page = self._pop_from_freelist()
        if recycled_page is not None:
            return recycled_page

        self.last_page += 1
        return self.last_page

    def _traverse_free_list(self) -> Tuple[Optional[FreelistNode], Optional[FreelistNode]]:
        """Walks the linked list of deallocated pages."""
        if self._freelist_start_page == 0:
            return None, None

        parent_node = None
        current_node = self.get_node(self._freelist_start_page)

        while current_node.next_page is not None:
            parent_node = current_node
            current_node = self.get_node(parent_node.next_page)

        return parent_node, current_node

    def _insert_in_freelist(self, page: int):
        """Marks a page as empty and adds it to the recycling pool."""
        _, tail_node = self._traverse_free_list()

        self.set_node(FreelistNode(self._tree_conf, page=page, next_page=None))

        if tail_node is None:
            self._freelist_start_page = page
            self.set_metadata(None, None)
        else:
            tail_node.next_page = page
            self.set_node(tail_node)

    def _pop_from_freelist(self) -> Optional[int]:
        """Claims a deallocated page from the recycling pool."""
        parent_node, tail_node = self._traverse_free_list()

        if tail_node is None:
            return None

        if parent_node is None:
            self._freelist_start_page = 0
            self.set_metadata(None, None)
        else:
            parent_node.next_page = None
            self.set_node(parent_node)

        return tail_node.page

    def get_metadata(self) -> tuple:
        """Reads Page 0, which holds the database configuration and root pointer."""
        try:
            meta_bytes = self._read_page(0)
        except ReachedEndOfFile:
            raise ValueError('Database is empty; metadata not initialized.')
            
        idx_root_end = PAGE_REFERENCE_BYTES
        found_root_page = int.from_bytes(meta_bytes[0:idx_root_end], ENDIAN)
        
        idx_page_size_end = idx_root_end + OTHERS_BYTES
        found_page_size = int.from_bytes(meta_bytes[idx_root_end:idx_page_size_end], ENDIAN)
        
        idx_order_end = idx_page_size_end + OTHERS_BYTES
        found_order = int.from_bytes(meta_bytes[idx_page_size_end:idx_order_end], ENDIAN)
        
        idx_key_end = idx_order_end + OTHERS_BYTES
        found_key_size = int.from_bytes(meta_bytes[idx_order_end:idx_key_end], ENDIAN)
        
        idx_val_end = idx_key_end + OTHERS_BYTES
        found_val_size = int.from_bytes(meta_bytes[idx_key_end:idx_val_end], ENDIAN)
        
        idx_freelist_end = idx_val_end + PAGE_REFERENCE_BYTES
        self._freelist_start_page = int.from_bytes(meta_bytes[idx_val_end:idx_freelist_end], ENDIAN)
        
        self._tree_conf = TreeConf(
            found_page_size, found_order, found_key_size, found_val_size, self._tree_conf.serializer
        )
        self._root_node_page = found_root_page
        return found_root_page, self._tree_conf

    def set_metadata(self, root_node_page: Optional[int], tree_conf: Optional[TreeConf]):
        """Writes the database configuration and root pointer to Page 0."""
        if root_node_page is None:
            root_node_page = self._root_node_page
        if tree_conf is None:
            tree_conf = self._tree_conf

        meta_length = 2 * PAGE_REFERENCE_BYTES + 4 * OTHERS_BYTES
        meta_payload = (
            root_node_page.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN) +
            tree_conf.page_size.to_bytes(OTHERS_BYTES, ENDIAN) +
            tree_conf.order.to_bytes(OTHERS_BYTES, ENDIAN) +
            tree_conf.key_size.to_bytes(OTHERS_BYTES, ENDIAN) +
            tree_conf.value_size.to_bytes(OTHERS_BYTES, ENDIAN) +
            self._freelist_start_page.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN) +
            bytes(tree_conf.page_size - meta_length) # Pad to fill Page 0 completely
        )
        self._write_page_in_tree(0, meta_payload, fsync=True)

        self._tree_conf = tree_conf
        self._root_node_page = root_node_page

    def close(self):
        """Safely shuts down the engine, moving all WAL data into the main database file."""
        self.perform_checkpoint()
        self._fd.close()
        if self._dir_fd is not None:
            os.close(self._dir_fd)

    def perform_checkpoint(self, reopen_wal=False):
        """Transfers committed data from the WAL into the permanent database file."""
        logger.info('Executing WAL checkpoint for %s', self._filename)
        for target_page, page_payload in self._wal.checkpoint():
            self._write_page_in_tree(target_page, page_payload, fsync=False)
            
        # Hardware sync ensures all pages transferred from WAL are physically safe
        fsync_file_and_dir(self._fd.fileno(), self._dir_fd)
        
        if reopen_wal:
            self._wal = WAL(self._filename, self._tree_conf.page_size)

    def _read_page(self, page: int) -> bytes:
        start_byte = page * self._tree_conf.page_size
        stop_byte = start_byte + self._tree_conf.page_size
        return read_from_file(self._fd, start_byte, stop_byte)

    def _write_page_in_tree(self, page: int, page_data: Union[bytes, bytearray], fsync: bool=True):
        """Directly writes a page to the main database file (bypassing WAL)."""
        assert len(page_data) == self._tree_conf.page_size
        self._fd.seek(page * self._tree_conf.page_size)
        write_to_file(self._fd, self._dir_fd, page_data, fsync=fsync)

    def __repr__(self):
        return '<FileMemory Engine: {}>'.format(self._filename)


# ==============================================================================
# WRITE-AHEAD LOG (WAL) IMPLEMENTATION
# ==============================================================================

class FrameType(enum.Enum):
    """Operation codes for the WAL log stream."""
    PAGE = 1
    COMMIT = 2
    ROLLBACK = 3


class WAL:
    """
    The Write-Ahead Log. 
    Protects the database from corruption during crashes by appending all writes 
    to a temporary log file first. Only when a 'COMMIT' frame is appended are 
    the writes considered finalized.
    """

    __slots__ = ['filename', '_fd', '_dir_fd', '_page_size',
                 '_committed_pages', '_not_committed_pages', 'needs_recovery']

    FRAME_HEADER_LENGTH = FRAME_TYPE_BYTES + PAGE_REFERENCE_BYTES

    def __init__(self, filename: str, page_size: int):
        self.filename = filename + '-wal'
        self._fd, self._dir_fd = open_file_in_dir(self.filename)
        self._page_size = page_size
        
        # Tracks pages that are safe vs pages currently in an active transaction
        self._committed_pages = dict()
        self._not_committed_pages = dict()

        self._fd.seek(0, io.SEEK_END)
        if self._fd.tell() == 0:
            self._create_header()
            self.needs_recovery = False
        else:
            logger.warning('Existing WAL file detected. Recovering from ungraceful shutdown.')
            self.needs_recovery = True
            self._load_wal()

    def checkpoint(self):
        """Yields all safely committed pages to be transferred to the main DB, then destroys the WAL."""
        if self._not_committed_pages:
            logger.warning('Discarding uncommitted transaction data during checkpoint.')

        fsync_file_and_dir(self._fd.fileno(), self._dir_fd)

        for page_id, file_offset in self._committed_pages.items():
            payload = read_from_file(
                self._fd, file_offset, file_offset + self._page_size
            )
            yield page_id, payload

        self._fd.close()
        os.unlink(self.filename)
        if self._dir_fd is not None:
            os.fsync(self._dir_fd)
            os.close(self._dir_fd)

    def _create_header(self):
        """Initializes a new WAL file with the system page size."""
        header_bytes = self._page_size.to_bytes(OTHERS_BYTES, ENDIAN)
        self._fd.seek(0)
        write_to_file(self._fd, self._dir_fd, header_bytes, True)

    def _load_wal(self):
        """Replays the log stream upon startup to recover committed data."""
        self._fd.seek(0)
        header_bytes = read_from_file(self._fd, 0, OTHERS_BYTES)
        assert int.from_bytes(header_bytes, ENDIAN) == self._page_size

        while True:
            try:
                self._load_next_frame()
            except ReachedEndOfFile:
                break
                
        if self._not_committed_pages:
            logger.warning('WAL contains an incomplete transaction. Rolling back automatically.')
            self._not_committed_pages = dict()

    def _load_next_frame(self):
        start_byte = self._fd.tell()
        stop_byte = start_byte + self.FRAME_HEADER_LENGTH
        frame_bytes = read_from_file(self._fd, start_byte, stop_byte)

        operation = int.from_bytes(frame_bytes[0:FRAME_TYPE_BYTES], ENDIAN)
        target_page = int.from_bytes(
            frame_bytes[FRAME_TYPE_BYTES:FRAME_TYPE_BYTES+PAGE_REFERENCE_BYTES],
            ENDIAN
        )

        frame_enum = FrameType(operation)
        if frame_enum is FrameType.PAGE:
            self._fd.seek(stop_byte + self._page_size)

        self._index_frame(frame_enum, target_page, stop_byte)

    def _index_frame(self, frame_enum: FrameType, target_page: int, payload_start: int):
        if frame_enum is FrameType.PAGE:
            self._not_committed_pages[target_page] = payload_start
        elif frame_enum is FrameType.COMMIT:
            self._committed_pages.update(self._not_committed_pages)
            self._not_committed_pages = dict()
        elif frame_enum is FrameType.ROLLBACK:
            self._not_committed_pages = dict()
        else:
            assert False, "Unknown WAL frame operation."

    def _add_frame(self, frame_enum: FrameType, target_page: Optional[int]=None,
                   page_payload: Optional[bytes]=None):
        """Appends an operation frame safely to the end of the log stream."""
        if frame_enum is FrameType.PAGE and (not target_page or not page_payload):
            raise ValueError('Cannot append a PAGE frame without page data.')
        if page_payload and len(page_payload) != self._page_size:
            raise ValueError('Payload size does not match configured page size.')
            
        if not target_page:
            target_page = 0
            
        if frame_enum is not FrameType.PAGE:
            page_payload = b''
            
        frame_bytes = (
            frame_enum.value.to_bytes(FRAME_TYPE_BYTES, ENDIAN) +
            target_page.to_bytes(PAGE_REFERENCE_BYTES, ENDIAN) +
            page_payload
        )
        
        self._fd.seek(0, io.SEEK_END)
        # Fsync immediately if it is a COMMIT/ROLLBACK to guarantee Atomicity
        write_to_file(self._fd, self._dir_fd, frame_bytes,
                      fsync=(frame_enum != FrameType.PAGE))
                      
        self._index_frame(frame_enum, target_page, self._fd.tell() - self._page_size)

    def get_page(self, page: int) -> Optional[bytes]:
        """Fetches the most recent version of a page from the WAL."""
        file_offset = None
        # Check active transaction first, then committed transactions
        for page_store in (self._not_committed_pages, self._committed_pages):
            file_offset = page_store.get(page)
            if file_offset:
                break

        if not file_offset:
            return None

        return read_from_file(self._fd, file_offset, file_offset + self._page_size)

    def set_page(self, page: int, page_payload: bytes):
        self._add_frame(FrameType.PAGE, page, page_payload)

    def commit(self):
        if self._not_committed_pages:
            self._add_frame(FrameType.COMMIT)

    def rollback(self):
        if self._not_committed_pages:
            self._add_frame(FrameType.ROLLBACK)

    def __repr__(self):
        return '<Write-Ahead Log: {}>'.format(self.filename)
