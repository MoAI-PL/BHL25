# Changelog

All notable changes to the "Green Coding Assistant" plugin will be documented in this file.

## [1.0.0] - 2025-11-29

### Added
- Initial release for Best Hack Hackathon 2025
- Real-time code analysis (EcoAnnotator) for Python files
  - Detection of inefficient `for` loops
  - Warning for file operations without context managers
  - Alert for wildcard imports
- CodeCarbon integration action (Alt+E)
  - Automatic import injection
  - Code wrapping with EmissionsTracker
  - Template insertion for non-selected code
- Support for PyCharm Community 2025.2.5
- Comprehensive documentation (README, INSTALL guide)
- Test examples for all features

### Technical Details
- Built with Kotlin and IntelliJ Platform SDK
- Package structure: `com.hackathon.eco`
- Minimum build: 252 (PyCharm 2025.2.5)
- Dependencies: Python module support

### Features
- **Annotator**: PSI-based static analysis
- **Action**: Document modification via WriteCommandAction
- **UI**: Editor popup menu integration
- **Shortcuts**: Alt+E keyboard shortcut

---

## [Unreleased]

### Planned
- Integration with actual eco-code-analyzer Python package
- Emissions dashboard
- Configurable rules
- Multi-language support

---

**Legend:**
- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security fixes
