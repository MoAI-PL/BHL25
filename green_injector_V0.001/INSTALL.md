# Green Coding Assistant - Installation Guide

## 📦 Installation

### Method 1: From Built Distribution
1. Build the plugin:
   ```bash
   ./gradlew buildPlugin
   ```

2. The plugin will be created at: `build/distributions/IntelliJ Platform Plugin Template-1.0.0.zip`

3. Install in PyCharm:
   - Open PyCharm Community 2025.2.5
   - Go to **Settings** → **Plugins**
   - Click the **⚙️ Gear Icon** → **Install Plugin from Disk...**
   - Select the `.zip` file
   - Restart PyCharm

### Method 2: Run from Source (Development Mode)
```bash
./gradlew runIde
```
This will launch a new PyCharm instance with the plugin pre-installed.

---

## 🚀 Features

### 1. **Real-Time Code Analysis** (Annotator)
The plugin automatically highlights inefficient Python code patterns:

- ⚡ **Inefficient Loops**: Detects `for i in range(...)` patterns
- 💧 **Resource Leaks**: Warns about `open()` without context managers
- 🗑️ **Memory Waste**: Flags wildcard imports (`from module import *`)

These warnings appear as you type, directly in the editor.

### 2. **CodeCarbon Integration** (Action)
Inject emissions tracking into your code:

- **Keyboard Shortcut**: `Alt+E`
- **Right-click Menu**: Select code → "Inject CodeCarbon Tracker"

#### How it works:
1. Select the code you want to measure
2. Press `Alt+E` or right-click → "Inject CodeCarbon Tracker"
3. The plugin will:
   - Add `from codecarbon import EmissionsTracker` import
   - Wrap your code with `with EmissionsTracker() as tracker:`

#### Example:
**Before:**
```python
def calculate():
    total = 0
    for i in range(1000000):
        total += i
    return total
```

**After (press Alt+E with code selected):**
```python
from codecarbon import EmissionsTracker

with EmissionsTracker() as tracker:
    def calculate():
        total = 0
        for i in range(1000000):
            total += i
        return total
```

---

## 📋 Prerequisites

To use the CodeCarbon feature, install the Python package:
```bash
pip install codecarbon
```

---

## 🧪 Testing the Plugin

1. Open the test file `test_example.py` in PyCharm
2. You should see warnings on:
   - Line 4: Inefficient loop
   - Line 8: File without context manager
   - Line 13: Wildcard import

3. Select lines 16-20 (the `calculate_sum` function)
4. Press `Alt+E`
5. The code will be wrapped with EmissionsTracker

---

## 🏗️ Project Structure

```
src/main/
├── kotlin/com/hackathon/eco/
│   ├── EcoAnnotator.kt    # Real-time code analysis
│   └── EcoRun.kt           # CodeCarbon injection action
└── resources/META-INF/
    └── plugin.xml          # Plugin configuration
```

---

## 🔧 Build from Source

```bash
# Clean build
./gradlew clean buildPlugin

# Run in development mode
./gradlew runIde

# Run tests
./gradlew test
```

---

## 📝 Technical Details

- **Platform**: IntelliJ Platform 2025.2.5
- **Target IDE**: PyCharm Community 2025.2.5
- **Language**: Kotlin
- **Min Build**: 252
- **Dependencies**: 
  - `com.intellij.modules.platform`
  - `com.intellij.modules.python`

---

## 🐛 Troubleshooting

### Plugin doesn't appear in PyCharm
- Verify PyCharm version is 2025.2.5
- Check that Python support is enabled
- Try: Settings → Plugins → ⚙️ → Check for updates

### Annotations don't show up
- Make sure you're editing a `.py` file
- Check Settings → Editor → Inspections → Python → "Eco-Code" warnings are enabled

### CodeCarbon import not found
Install the package:
```bash
pip install codecarbon
```

---

## 🎯 Hackathon Context

This plugin addresses the problem of **inefficient code being deployed to computing clusters**, which wastes energy and increases carbon emissions.

**Solution**: 
- Developers get real-time feedback on code efficiency
- Automatic emissions tracking integration helps measure and optimize code before deployment
- Reduces unnecessary computation in production environments

---

## 📄 License

MIT License - Created for Best Hack Hackathon 2025

