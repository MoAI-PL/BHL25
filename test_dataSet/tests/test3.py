data = list(range(2000))
count = 0
for i in data:
    for j in data:
        for k in data:
            if i + j + k == 10000:
                count += 1
