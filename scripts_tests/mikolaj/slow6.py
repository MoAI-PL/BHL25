# slow6.py
import numpy as np

for _ in range(150):
    A = np.random.rand(800, 800)
    B = A @ A
print("done")
