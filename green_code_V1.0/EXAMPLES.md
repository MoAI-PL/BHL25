# Before & After Examples

## Example 1: Loop Optimization

### ❌ Before (Inefficient)
```python
# ⚡ Warning: Inefficient Loop Detected
total = 0
for i in range(1000000):
    total += i * 2
print(total)
```

### ✅ After (Optimized)
```python
# No warnings - using generator expression
total = sum(i * 2 for i in range(1000000))
print(total)

# Even better - using NumPy
import numpy as np
arr = np.arange(1000000)
total = (arr * 2).sum()
print(total)
```

**Energy Savings**: ~40% less CPU cycles

---

## Example 2: File Operations

### ❌ Before (Resource Leak)
```python
# 💧 Warning: Resource Leak Risk
file = open("data.txt", "w")
file.write("Hello")
file.close()  # What if an exception occurs before this?
```

### ✅ After (Safe & Efficient)
```python
# No warnings - using context manager
with open("data.txt", "w") as file:
    file.write("Hello")
# File automatically closed, even if exception occurs
```

**Benefits**: 
- Prevents resource leaks
- Reduces OS overhead
- Automatic cleanup

---

## Example 3: Import Optimization

### ❌ Before (Memory Waste)
```python
# 🗑️ Warning: Memory Waste
from os import *
from sys import *
from math import *
```

### ✅ After (Efficient)
```python
# No warnings - specific imports
from os import path, environ
from sys import argv
from math import sqrt, pi
```

**Memory Savings**: Only loads needed functions

---

## Example 4: CodeCarbon Integration

### Before CodeCarbon
```python
def train_model(data):
    model = create_model()
    model.fit(data)
    return model

result = train_model(my_data)
# ❓ How much energy did this consume?
# ❓ What's the carbon footprint?
```

### After CodeCarbon (Alt+E)
```python
from codecarbon import EmissionsTracker

with EmissionsTracker() as tracker:
    def train_model(data):
        model = create_model()
        model.fit(data)
        return model
    
    result = train_model(my_data)

# ✅ emissions.csv now contains:
# - timestamp
# - duration (seconds)
# - energy_consumed (kWh)
# - emissions (kg CO2)
```

**Output Example** (emissions.csv):
```csv
timestamp,project_name,duration,emissions,energy_consumed
2025-11-29 21:30:45,my_project,12.5,0.0025,0.005
```

---

## Real-World Impact

### Scenario: Training ML Model Daily

**Before Optimization:**
- Runtime: 2 hours
- Energy: 0.5 kWh
- CO2: ~0.25 kg
- **Annual**: 91.25 kg CO2 (≈ 400 km in a car)

**After Optimization:**
- Runtime: 1.2 hours (40% faster)
- Energy: 0.3 kWh
- CO2: ~0.15 kg
- **Annual**: 54.75 kg CO2

**Savings**: 36.5 kg CO2/year per developer!

---

## How to Achieve This

1. Install Green Coding Assistant plugin
2. Open your Python files
3. Look for ⚡💧🗑️ warnings
4. Apply suggested optimizations
5. Use Alt+E to measure improvements
6. Compare before/after emissions!

**Every optimization counts! 🌱**

