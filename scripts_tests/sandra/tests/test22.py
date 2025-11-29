lst = list(range(5000))
for i in lst:
    if i in set(lst):
        pass

print("Inefficient membership check done")
