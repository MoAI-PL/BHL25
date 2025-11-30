# 🌱 Green Coding Assistant

![PyCharm](https://img.shields.io/badge/PyCharm-2025.2.5-green)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9+-purple)
![License](https://img.shields.io/badge/license-MIT-blue)

**A PyCharm plugin that helps developers write energy-efficient Python code by integrating sustainability metrics directly into the coding workflow.**

Created for **Best Hack Hackathon 2025** 🏆

---

## 🎯 Problem

**Developers often deploy inefficient code to computing clusters**, leading to:
- ⚡ Wasted computational resources
- 💰 Increased operational costs
- 🌍 Unnecessary carbon emissions

Code that could be optimized before deployment runs on expensive hardware, consuming energy for no reason.

---

## 💡 Our Solution

**Green Coding Assistant** is a PyCharm plugin that **evolves your code before it reaches production clusters**. It provides:

1. **Real-time code analysis** - Highlights inefficient patterns as you type
2. **Automated emissions tracking** - Integrates CodeCarbon with one keystroke
3. **Actionable suggestions** - Practical tips to reduce energy consumption

### How It Works

```
Developer writes code → Plugin analyzes → Suggests optimizations → Developer improves code → Deploy efficient code to cluster
```

**Result**: Less wasted computation, lower energy costs, reduced carbon footprint.

---

## ✨ Features

### 1. Real-Time Static Analysis (Annotator)

The plugin highlights inefficient code patterns directly in the editor:

| Pattern | Warning | Suggestion |
|---------|---------|------------|
| `for i in range(...)` | ⚡ Inefficient Loop | Use NumPy vectorization or list comprehension |
| `file = open(...)` | 💧 Resource Leak Risk | Use `with open(...)` context manager |
| `from module import *` | 🗑️ Memory Waste | Import only what you need |

![Annotation Example](https://via.placeholder.com/800x200.png?text=Real-time+warnings+in+editor)

### 2. CodeCarbon Integration (Action)

**Keyboard Shortcut**: `Alt+E`

Automatically wraps your code with emissions tracking:

**Before:**
```python
def calculate():
    total = sum(range(1000000))
    return total
```

**After** (press Alt+E with code selected):
```python
from codecarbon import EmissionsTracker

with EmissionsTracker() as tracker:
    def calculate():
        total = sum(range(1000000))
        return total
```

Now when you run the script, CodeCarbon will measure and report:
- Energy consumed (kWh)
- Carbon emissions (kg CO2)
- Runtime duration

---

## 📦 Installation

### Quick Install

1. Download the latest release from [Releases](https://github.com/TwojLogin/Eco-Plugin/releases)
2. In PyCharm: **Settings → Plugins → ⚙️ → Install Plugin from Disk...**
3. Select the `.zip` file and restart PyCharm

### Build from Source

```bash
git clone https://github.com/TwojLogin/Eco-Plugin.git
cd Eco-Plugin
./gradlew buildPlugin
```

The plugin will be in `build/distributions/`.

**See [INSTALL.md](INSTALL.md) for detailed instructions.**

---

## 🚀 Quick Start

1. Install the plugin
2. Install CodeCarbon: `pip install codecarbon`
3. Open a Python file in PyCharm
4. Write some code (you'll see warnings for inefficient patterns)
5. Select code → Press `Alt+E` → Run script to see emissions

**Try it with the included test file**: `test_example.py`

---

## 🏗️ Technical Stack

- **Language**: Kotlin
- **Platform**: IntelliJ Platform 2025.2.5
- **Target IDE**: PyCharm Community 2025.2.5
- **Analysis Tools**: 
  - Custom PSI-based static analysis (simulates eco-code-analyzer)
  - CodeCarbon integration for runtime emissions tracking

### Architecture

```
┌─────────────────────────────────────┐
│         PyCharm Editor              │
├─────────────────────────────────────┤
│  EcoAnnotator (Real-time Analysis) │
│  - Scans PSI tree                   │
│  - Highlights inefficiencies        │
├─────────────────────────────────────┤
│  EcoRun (Action Handler)            │
│  - Injects CodeCarbon wrapper       │
│  - Manages imports                  │
└─────────────────────────────────────┘
```

---

## 📊 Impact

### For Developers
- ⏱️ **Faster feedback** - Catch inefficiencies before code review
- 📈 **Measurable improvements** - See actual energy/carbon metrics
- 🎓 **Learn best practices** - Tooltip suggestions guide better coding

### For Organizations
- 💰 **Cost savings** - Reduce cluster computation time
- 🌍 **Sustainability** - Lower carbon footprint of IT operations
- 📉 **Resource optimization** - Deploy only efficient code

---

## 🧪 Testing

The plugin includes test cases for common anti-patterns:

```bash
# Run tests
./gradlew test

# Run in development mode
./gradlew runIde
```

Open `test_example.py` to see all features in action.

---

## 🛣️ Roadmap

- [ ] Integration with real `eco-code-analyzer` Python package
- [ ] Dashboard showing aggregate emissions across projects
- [ ] GitHub Actions integration for CI/CD checks
- [ ] Support for more languages (Java, JavaScript)
- [ ] Custom rule configuration
- [ ] Team-wide analytics

---

## 🤝 Contributing

Built during Best Hack Hackathon 2025. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 👥 Team

**MoAI** - Best Hack Hackathon 2025

---

## 📚 References

- [CodeCarbon](https://github.com/mlco2/codecarbon) - Python library for tracking CO2 emissions
- [eco-code](https://github.com/green-code-initiative/ecoCode) - Static analysis for energy-efficient code
- [IntelliJ Platform SDK](https://plugins.jetbrains.com/docs/intellij/) - Plugin development documentation

---

## 🙏 Acknowledgments

Special thanks to:
- JetBrains for the IntelliJ Platform
- CodeCarbon project for emissions tracking
- Green Code Initiative for eco-code-analyzer
- Best Hack Hackathon organizers

---

**Made with 💚 for a greener future**

