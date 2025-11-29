def intersect(a, b):
    out = []
    for x in a:
        for y in b:
            if x == y:
                out.append(x)
    return out

print(intersect([1,2,3], [2,3,4]))
