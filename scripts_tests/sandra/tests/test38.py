s = "abcdefgh" * 5000
rev = ""
for c in s:
    rev = c + rev

print(len(rev))
