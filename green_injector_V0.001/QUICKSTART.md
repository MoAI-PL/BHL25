# 🚀 Quick Start Guide - Green Coding Assistant

## 5-Minute Setup

### Step 1: Install the Plugin (2 min)

```bash
# Build the plugin
./gradlew buildPlugin

# The plugin is now at: build/distributions/IntelliJ Platform Plugin Template-1.0.0.zip
```

In PyCharm:
1. Open **Settings** (Ctrl+Alt+S / Cmd+,)
2. Go to **Plugins**
3. Click **⚙️ (Gear Icon)** → **Install Plugin from Disk...**
4. Select the `.zip` file
5. Click **OK** and **Restart PyCharm**

### Step 2: Install CodeCarbon (1 min)

```bash
pip install codecarbon
```

### Step 3: Try It! (2 min)

1. Open `demo.py` in PyCharm
2. You'll see warnings highlighted:
   - Line 21: ⚡ Inefficient Loop
   - Line 32: 💧 Resource Leak
   - Line 40: 🗑️ Memory Waste

3. Select lines 54-60 (the `heavy_computation` function)
4. Press **Alt+E**
5. Run the script: `python demo.py`
6. Check `emissions.csv` for carbon footprint!

---

## Common Issues

### "Plugin doesn't load"
- ✅ Check PyCharm version: **2025.2.5**
- ✅ Ensure Python plugin is enabled

### "No warnings appear"
- ✅ Open a `.py` file
- ✅ Check Editor → Inspections → Python

### "Alt+E does nothing"
- ✅ Restart PyCharm after installation
- ✅ Try right-click → "Inject CodeCarbon Tracker"

---

## What's Next?

- Read [INSTALL.md](INSTALL.md) for detailed setup
- Read [README_PLUGIN.md](README_PLUGIN.md) for full documentation
- Explore `test_example.py` for more examples

---

**Need help?** Open an issue on GitHub!

