# slow1.py
import math
import time

x = 1.000001
for i in range(50_000_000):
    x = math.tan(x) ** 2 + math.sqrt(abs(x))
print("done")
