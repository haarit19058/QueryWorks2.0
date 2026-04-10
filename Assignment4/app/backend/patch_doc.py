with open("main.py", "r") as f:
    text = f.read()

text = text.replace("MD5 hash", "SHA-256 hash")

with open("main.py", "w") as f:
    f.write(text)
