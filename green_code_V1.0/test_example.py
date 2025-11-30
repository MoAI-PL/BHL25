import time

# Test 1: Inefficient loop
for i in range(1000):
    x = i * 2

# Test 2: File without context manager
file = open("test.txt", "w")
file.write("test")
file.close()

# Test 3: Wildcard import
from os import *

# Test 4: Code to wrap with CodeCarbon
def calculate_sum():
    total = 0
    for i in range(1000000):
        total += i
    return total

result = calculate_sum()
print(f"Result: {result}")

