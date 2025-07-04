#!/usr/bin/env python3
"""
Build script for md2notion package
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def clean_build():
    """Clean build artifacts"""
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
            else:
                print(f"Removing {path}")
                path.unlink()

def build_package():
    """Build the package"""
    print("Building md2notion package...")
    
    # Clean previous builds
    clean_build()
    
    # Build source distribution
    if not run_command("python setup.py sdist"):
        return False
    
    # Build wheel
    if not run_command("python setup.py bdist_wheel"):
        return False
    
    print("Build completed successfully!")
    return True

def test_installation():
    """Test the installation"""
    print("Testing installation...")
    
    # Install in a test environment
    if not run_command("pip install dist/*.whl"):
        return False
    
    # Test the command
    if not run_command("md2notion --help"):
        return False
    
    print("Installation test passed!")
    return True

def main():
    """Main build process"""
    print("=== md2notion Build Script ===")
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("Error: setup.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Build the package
    if not build_package():
        print("Build failed!")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("Installation test failed!")
        sys.exit(1)
    
    print("\n=== Build Summary ===")
    print("✅ Package built successfully")
    print("✅ Installation test passed")
    print("\nDistribution files created:")
    for path in Path("dist").glob("*"):
        print(f"  - {path}")
    
    print("\nTo install the package:")
    print("  pip install dist/*.whl")
    
    print("\nTo upload to PyPI:")
    print("  twine upload dist/*")

if __name__ == "__main__":
    main() 