with open("large.txt") as f:
    for _ in range(10000):
        f.seek(0)     # cofanie na początek 10000 razy = dramat
        for line in f:
            pass
