# slow3.py
text = "a" * 1_000_000

for _ in range(200):
    text = text.replace("a", "aa")[:1_000_000]

print("ok")
