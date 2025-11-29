import random
lst = list(range(3000))
while lst:
    lst.pop(random.randint(0, len(lst) - 1))

print("Random pop OK")

