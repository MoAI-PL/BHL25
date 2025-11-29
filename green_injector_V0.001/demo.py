"""
Green Coding Assistant - Demo Script
=====================================

This file demonstrates all features of the Green Coding Assistant plugin.
Open this file in PyCharm with the plugin installed to see:
1. Real-time warnings (annotations)
2. CodeCarbon integration (Alt+E)

Prerequisites:
- PyCharm Community 2025.2.5 with Green Coding Assistant plugin
- pip install codecarbon
"""

# ============================================
# SECTION 1: INEFFICIENT LOOP DETECTION
# ============================================
# The plugin will warn you about this loop
# Suggestion: Use NumPy or list comprehension

print("Demo 1: Inefficient Loop")
total = 0
for i in range(1000000):  # ⚡ Warning should appear here
    total += i * 2
print(f"Total: {total}")


# ============================================
# SECTION 2: RESOURCE LEAK DETECTION
# ============================================
# The plugin will warn about file not using context manager
# Suggestion: Use 'with open(...)' instead

print("\nDemo 2: Resource Leak")
file = open("demo.txt", "w")  # 💧 Warning should appear here
file.write("Hello, Green Coding!")
file.close()


# ============================================
# SECTION 3: WILDCARD IMPORT DETECTION
# ============================================
# The plugin will warn about importing everything
# Suggestion: Import only what you need

print("\nDemo 3: Memory Waste")
from math import *  # 🗑️ Warning should appear here
result = sqrt(16)
print(f"Square root: {result}")


# ============================================
# SECTION 4: CODECARBON INTEGRATION DEMO
# ============================================
# To test CodeCarbon injection:
# 1. Select the code below (lines 54-60)
# 2. Press Alt+E
# 3. The plugin will wrap it with EmissionsTracker
# 4. Run the script to see actual emissions!

print("\nDemo 4: CodeCarbon Integration")
def heavy_computation():
    """This function does intensive computation"""
    result = 0
    for i in range(5000000):
        result += i ** 2
    return result

output = heavy_computation()
print(f"Computation result: {output}")


# ============================================
# SECTION 5: BEST PRACTICES (No Warnings)
# ============================================
# These examples show how to write efficient code
# No warnings should appear here!

print("\n✅ Best Practices:")

# Good: List comprehension instead of loop
efficient_total = sum(i * 2 for i in range(1000000))
print(f"Efficient total: {efficient_total}")

# Good: Context manager for files
with open("demo_good.txt", "w") as f:
    f.write("This is energy efficient!")
print("File written efficiently")

# Good: Specific imports
from math import sqrt as math_sqrt
good_result = math_sqrt(25)
print(f"Square root (efficient): {good_result}")


# ============================================
# HOW TO USE THIS DEMO
# ============================================
"""
Step 1: Open this file in PyCharm
Step 2: Look for colored warnings on lines 21, 32, 40
Step 3: Hover over warnings to see tooltips
Step 4: Select lines 54-60 (heavy_computation function)
Step 5: Press Alt+E to inject CodeCarbon tracker
Step 6: Run the script: python demo.py
Step 7: Check the emissions.csv file created by CodeCarbon

Expected Output:
- Console will show all demo results
- emissions.csv will contain carbon footprint data
- You'll see energy consumed and CO2 emitted!
"""

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Green Coding Assistant Demo Complete!")
    print("="*50)

