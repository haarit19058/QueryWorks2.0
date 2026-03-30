"""
Data serialization strategies for the B+ Tree.

Since the persistent storage engine (the disk) only understands raw binary data, 
we need a standard way to translate Python objects (like integers, strings, or UUIDs) 
into fixed-length byte arrays and back again.
"""
import abc
from datetime import datetime, timezone
from uuid import UUID

# Attempt to load the temporenc library for compact datetime serialization
try:
    import temporenc
except ImportError:
    temporenc = None

from .const import ENDIAN


class Serializer(metaclass=abc.ABCMeta):
    """
    Abstract base class establishing the contract for all serializers.
    Any custom data type you want to use as a key in the B+ Tree must implement this.
    """

    __slots__ = []

    @abc.abstractmethod
    def serialize(self, obj: object, key_size: int) -> bytes:
        """Convert a Python object into a raw byte sequence for disk storage."""

    @abc.abstractmethod
    def deserialize(self, data: bytes) -> object:
        """Reconstruct the original Python object from a raw byte sequence."""

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class IntSerializer(Serializer):
    """
    Translates integer keys into binary. 
    It relies on the system's configured ENDIANness to ensure that the 
    bytes are ordered correctly for both saving and reading.
    """

    __slots__ = []

    def serialize(self, obj: int, key_size: int) -> bytes:
        return obj.to_bytes(key_size, ENDIAN)

    def deserialize(self, data: bytes) -> int:
        return int.from_bytes(data, ENDIAN)


class StrSerializer(Serializer):
    """
    Encodes standard Python strings into UTF-8 byte arrays.
    It includes a safety assertion to guarantee that the resulting byte payload
    does not exceed the database's configured maximum key size.
    """

    __slots__ = []

    def serialize(self, obj: str, key_size: int) -> bytes:
        encoded_string = obj.encode(encoding='utf-8')
        assert len(encoded_string) <= key_size, "String exceeds maximum key size"
        return encoded_string

    def deserialize(self, data: bytes) -> str:
        return data.decode(encoding='utf-8')


class UUIDSerializer(Serializer):
    """
    Efficiently extracts the underlying 16-byte binary representation 
    of a standard UUID object.
    """

    __slots__ = []

    def serialize(self, obj: UUID, key_size: int) -> bytes:
        return obj.bytes

    def deserialize(self, data: bytes) -> UUID:
        return UUID(bytes=data)


class DatetimeUTCSerializer(Serializer):
    """
    Converts timezone-aware datetime objects into a compact binary format.
    Requires the third-party 'temporenc' library.
    """

    __slots__ = []

    def __init__(self):
        if temporenc is None:
            raise RuntimeError(
                'The third-party library "temporenc" is required to serialize datetime objects.'
            )

    def serialize(self, obj: datetime, key_size: int) -> bytes:
        # We strictly enforce timezone awareness to prevent data corruption across servers
        if obj.tzinfo is None:
            raise ValueError('DatetimeUTCSerializer requires a timezone-aware datetime object.')
        
        return temporenc.packb(obj, type='DTS')

    def deserialize(self, data: bytes) -> datetime:
        unpacked_dt = temporenc.unpackb(data).datetime()
        # Ensure the reconstructed object is explicitly set to UTC
        return unpacked_dt.replace(tzinfo=timezone.utc)
