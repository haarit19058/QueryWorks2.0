

import hashlib

def get_shard_id(member_id: int) -> int:
    """Computes the shard ID using SHA-256 hash of the MemberID modulo 3"""
    hash_digest = hashlib.sha256(str(member_id).encode()).hexdigest()
    return int(hash_digest, 16) % 3


print(get_shard_id(28498491))  # Example usage