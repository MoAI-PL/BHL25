# slow9.py
import time

value = 0
for i in range(1_000_000):
    value += (i ** 0.5)
    if i % 5000 == 0:
        time.sleep(0.001)

print("finished")
