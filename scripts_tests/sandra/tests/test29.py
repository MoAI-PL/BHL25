def count_chars(s):
    result = {}
    for c in s:
        count = 0
        for d in s:
            if d == c:
                count += 1
        result[c] = count
    return result

print(count_chars("abca"))

