def counter(arr):
    d = {}
    for x in arr:
        if x not in d:
            d[x] = 0
        d[x] += 1
    return d

print(counter([1,2,2,3,3,3]))

