#!/usr/bin/env python3
"""
Dependency checker for Gold & Silver Agent System
"""
import sys

REQUIRED_PACKAGES = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'yfinance': 'yfinance',
    'requests': 'requests',
}

OPTIONAL_PACKAGES = {
    'dotenv': 'python-dotenv',
    'fredapi': 'fredapi',
    'openai': 'openai',
}

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def main():
    print("="*60)
    print("Gold & Silver Agent System - Dependency Check")
    print("="*60)
    print()
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    print("Checking required packages...")
    for package, import_name in REQUIRED_PACKAGES.items():
        if check_package(package, import_name):
            print(f"  ✓ {package}")
        else:
            print(f"  ✗ {package} - MISSING")
            missing_required.append(package)
    
    print()
    print("Checking optional packages...")
    for package, import_name in OPTIONAL_PACKAGES.items():
        if check_package(package, import_name):
            print(f"  ✓ {package}")
        else:
            print(f"  ✗ {package} - MISSING (optional)")
            missing_optional.append(package)
    
    print()
    print("="*60)
    
    if missing_required:
        print("ERROR: Missing required packages!")
        print()
        print("Please install missing packages:")
        print(f"  pip install {' '.join([REQUIRED_PACKAGES[p] for p in missing_required])}")
        print()
        print("Or install all dependencies:")
        print("  pip install -r requirements.txt")
        print()
        return 1
    else:
        print("✓ All required packages are installed!")
        if missing_optional:
            print()
            print("Optional packages missing (system will work but with limited features):")
            for pkg in missing_optional:
                print(f"  - {pkg}: pip install {OPTIONAL_PACKAGES[pkg]}")
        print()
        return 0

if __name__ == "__main__":
    sys.exit(main())



