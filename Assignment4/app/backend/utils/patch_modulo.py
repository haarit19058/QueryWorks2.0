import re

with open("main.py", "r") as f:
    content = f.read()

content = content.replace("hashlib.md5(str(member_id).encode()).hexdigest()", "hashlib.sha256(str(member_id).encode()).hexdigest()")
content = content.replace("int(test_user_id) % 3", "get_shard_id(int(test_user_id))")
content = content.replace("shard_id = member_id % 3", "shard_id = get_shard_id(member_id)")
content = content.replace("shard_target = next_id % 3", "shard_target = get_shard_id(next_id)")
content = content.replace("user.MemberID % 3", "get_shard_id(user.MemberID)")
content = content.replace("p.PassengerID % 3", "get_shard_id(p.PassengerID)")
content = content.replace("data.ReceiverMemberID % 3", "get_shard_id(data.ReceiverMemberID)")
content = content.replace("p_id % 3", "get_shard_id(p_id)")
content = content.replace("req.PassengerID % 3", "get_shard_id(req.PassengerID)")
content = content.replace("sender_id % 3", "get_shard_id(sender_id)")

# Edge cases
content = content.replace("shard_id = member_id % 3", "shard_id = get_shard_id(member_id)") # if missed

with open("main.py", "w") as f:
    f.write(content)
