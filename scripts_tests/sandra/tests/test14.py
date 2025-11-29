def unique(arr):
    out = []
    for x in arr:
        if x not in out:
            out.append(x)
    return out

print(unique([1,1,2,3,3,4]))
