#!/usr/bin/env python3
"""
Setup script for Green Coding Assistant dependencies.
Run this script to install required Python packages.
"""
import subprocess
import sys
import json


def check_and_install_dependencies():
    """Check and install required dependencies."""
    results = {
        'codecarbon': {'installed': False, 'version': None, 'error': None},
        'eco_code_analyzer': {'installed': False, 'version': None, 'error': None},
        'psutil': {'installed': False, 'version': None, 'error': None}
    }
    
    # Check CodeCarbon
    try:
        import codecarbon
        results['codecarbon']['installed'] = True
        results['codecarbon']['version'] = getattr(codecarbon, '__version__', 'unknown')
    except ImportError:
        results['codecarbon']['error'] = 'Not installed'
    
    # Check eco-code-analyzer
    try:
        import eco_code_analyzer
        results['eco_code_analyzer']['installed'] = True
        results['eco_code_analyzer']['version'] = getattr(eco_code_analyzer, '__version__', 'unknown')
    except ImportError:
        results['eco_code_analyzer']['error'] = 'Not installed'
    
    # Check psutil
    try:
        import psutil
        results['psutil']['installed'] = True
        results['psutil']['version'] = getattr(psutil, '__version__', 'unknown')
    except ImportError:
        results['psutil']['error'] = 'Not installed (optional)'
    
    return results


def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', package_name, '--quiet'
        ])
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)


def main():
    """Main entry point."""
    if '--check' in sys.argv:
        # Just check status
        results = check_and_install_dependencies()
        print(json.dumps(results, indent=2))
        return
    
    if '--install' in sys.argv:
        # Install missing dependencies
        print("Installing Green Coding Assistant dependencies...")
        
        packages = ['codecarbon', 'eco-code-analyzer', 'psutil']
        
        for package in packages:
            print(f"  Installing {package}...", end=' ')
            success, error = install_package(package)
            if success:
                print("OK")
            else:
                print(f"FAILED: {error}")
        
        print("\nVerifying installation...")
        results = check_and_install_dependencies()
        print(json.dumps(results, indent=2))
        return
    
    # Default: print help
    print("Green Coding Assistant - Dependency Setup")
    print("-" * 40)
    print("Usage:")
    print(f"  {sys.executable} setup_dependencies.py --check    Check installed packages")
    print(f"  {sys.executable} setup_dependencies.py --install  Install required packages")
    print()
    print("Or install manually:")
    print("  pip install codecarbon eco-code-analyzer psutil")


if __name__ == '__main__':
    main()

