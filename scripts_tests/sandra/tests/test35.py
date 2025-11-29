def indices(lst):
    out = []
    idx = 0
    for _ in lst:
        out.append(idx)
        idx += 1
    return out

print(indices(['a','b','c']))
