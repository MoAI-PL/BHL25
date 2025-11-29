def squares(n):
    out = []
    for i in range(n):
        for j in range(i):
            if j == i - 1:
                out.append(i * i)
    return out

print(squares(10))