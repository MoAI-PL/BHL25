def dedup(lst):
    result = []
    for x in lst:
        exists = False
        for y in result:
            if x == y:
                exists = True
        if not exists:
            result.append(x)
    return result

print(dedup([1,2,2,3,3,4]))
