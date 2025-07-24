#!/usr/bin/env python3
"""
BLS Package Setup
=================

Sets up the BLS data package for system-wide use.
This allows you to import the BLS package from any Python project.

Usage:
    python setup_package.py           # Install to site-packages
    python setup_package.py --local   # Install to user directory
    python setup_package.py --dev     # Development install (symlink)
"""

import os
import sys
import shutil
import site
from pathlib import Path
import tempfile


def get_install_locations():
    """Get possible installation locations"""
    locations = {
        'user': Path(site.getusersitepackages()) if hasattr(site, 'getusersitepackages') else None,
        'system': Path(site.getsitepackages()[0]) if site.getsitepackages() else None,
        'local': Path.cwd() / "dist" / "bls_data"
    }
    
    # Add user site packages if it exists
    try:
        import sysconfig
        user_site = sysconfig.get_path('purelib', scheme='posix_user')
        if user_site:
            locations['user_alt'] = Path(user_site)
    except:
        pass
    
    return locations


def create_package_structure(package_dir: Path):
    """Create the package structure with necessary files"""
    print(f"📦 Creating package structure in {package_dir}")
    
    # Create package directory
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy main module
    source_file = Path(__file__).parent / "bls_package.py"
    dest_file = package_dir / "__init__.py"
    
    print(f"   📄 Copying {source_file.name} → {dest_file.name}")
    shutil.copy2(source_file, dest_file)
    
    # Create setup.py for proper package installation
    setup_py_content = '''
from setuptools import setup, find_packages

setup(
    name="bls-data",
    version="1.0.0",
    description="Bureau of Labor Statistics Data Loader",
    author="BLS Scraper API",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "python-dateutil>=2.8.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
'''
    
    setup_file = package_dir.parent / "setup.py"
    with open(setup_file, 'w') as f:
        f.write(setup_py_content.strip())
    
    print(f"   📄 Created setup.py")
    
    return True


def install_to_location(package_name: str, install_path: Path):
    """Install package to specific location"""
    try:
        # Create target directory
        target_dir = install_path / package_name
        
        print(f"📥 Installing to {target_dir}")
        
        # Ensure parent directory exists and is writable
        install_path.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = install_path / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            raise PermissionError(f"No write permission to {install_path}")
        
        # Create the package
        success = create_package_structure(target_dir)
        
        if success:
            print(f"✅ Successfully installed to {target_dir}")
            return target_dir
        else:
            print(f"❌ Failed to create package structure")
            return None
            
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return None


def create_example_notebook():
    """Create an example Jupyter notebook"""
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# BLS Data Analysis Example\n",
                    "\n",
                    "This notebook demonstrates how to use the BLS data package to analyze Consumer Price Index (CPI) data.\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Import the BLS data package\n",
                    "from bls_data import load_data, load_data_to_dataframe, get_available_categories\n",
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "\n",
                    "print('📊 BLS Data Package loaded successfully!')"
                ],
                "outputs": []
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Define categories to analyze\n",
                    "categories = [\n",
                    "    'All items',\n",
                    "    'Food',\n",
                    "    'Energy', \n",
                    "    'Shelter',\n",
                    "    'Transportation'\n",
                    "]\n",
                    "\n",
                    "print(f'📋 Analyzing {len(categories)} categories:')\n",
                    "for i, cat in enumerate(categories, 1):\n",
                    "    print(f'   {i}. {cat}')"
                ],
                "outputs": []
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Load data for June 2025\n",
                    "df = load_data_to_dataframe(categories, '2025-06')\n",
                    "\n",
                    "# Display the data\n",
                    "print('📈 CPI Data for June 2025:')\n",
                    "print(df[['category', 'nsa_previous_month', 'nsa_current_month']].to_string(index=False))"
                ],
                "outputs": []
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Calculate month-over-month change\n",
                    "df['mom_change_pct'] = ((df['nsa_current_month'] - df['nsa_previous_month']) / df['nsa_previous_month'] * 100).round(2)\n",
                    "\n",
                    "print('📊 Month-over-Month Inflation Analysis:')\n",
                    "print(df[['category', 'mom_change_pct']].to_string(index=False))"
                ],
                "outputs": []
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Create a visualization\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "\n",
                    "# Bar chart of month-over-month changes\n",
                    "plt.subplot(1, 2, 1)\n",
                    "colors = ['red' if x > 0 else 'green' for x in df['mom_change_pct']]\n",
                    "plt.barh(df['category'], df['mom_change_pct'], color=colors, alpha=0.7)\n",
                    "plt.xlabel('Month-over-Month Change (%)')\n",
                    "plt.title('CPI Inflation by Category')\n",
                    "plt.grid(axis='x', alpha=0.3)\n",
                    "\n",
                    "# Current vs Previous month comparison\n",
                    "plt.subplot(1, 2, 2)\n",
                    "x = range(len(df))\n",
                    "plt.plot(x, df['nsa_previous_month'], 'o-', label='Previous Month', marker='o')\n",
                    "plt.plot(x, df['nsa_current_month'], 's-', label='Current Month', marker='s')\n",
                    "plt.xticks(x, df['category'], rotation=45, ha='right')\n",
                    "plt.ylabel('CPI Index Value')\n",
                    "plt.title('CPI Index Values Comparison')\n",
                    "plt.legend()\n",
                    "plt.grid(alpha=0.3)\n",
                    "\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ],
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Available Categories\n",
                    "\n",
                    "You can see all available categories in the Excel file:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Show available categories\n",
                    "available_cats = get_available_categories(15)\n",
                    "\n",
                    "print('📋 Available Categories (first 15):')\n",
                    "for i, cat in enumerate(available_cats, 1):\n",
                    "    print(f'   {i:2d}. {cat}')"
                ],
                "outputs": []
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    import json
    
    notebook_file = Path(__file__).parent / "example_bls_analysis.ipynb"
    with open(notebook_file, 'w') as f:
        json.dump(notebook_content, f, indent=2)
    
    print(f"📓 Created example notebook: {notebook_file}")
    return notebook_file


def main():
    """Main setup function"""
    print("🔧 BLS Package Setup")
    print("=" * 50)
    
    # Check command line arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    dev_mode = "--dev" in args
    local_mode = "--local" in args
    
    # Get installation locations
    locations = get_install_locations()
    
    package_name = "bls_data"
    installed_location = None
    
    # Choose installation method
    if dev_mode:
        print("🔗 Development mode: Creating symlink")
        # For dev mode, create symlink in current directory
        target_dir = Path.cwd() / package_name
        source_file = Path(__file__).parent / "bls_package.py"
        init_file = target_dir / "__init__.py"
        
        target_dir.mkdir(exist_ok=True)
        if init_file.exists():
            init_file.unlink()
        
        try:
            init_file.symlink_to(source_file.absolute())
            installed_location = target_dir
            print(f"✅ Development symlink created: {installed_location}")
        except OSError:
            # Fallback to copy if symlink fails
            shutil.copy2(source_file, init_file)
            installed_location = target_dir
            print(f"✅ Development copy created: {installed_location}")
    
    elif local_mode:
        print("📁 Local installation mode")
        installed_location = install_to_location(package_name, locations['local'])
    
    else:
        print("🌐 System installation mode")
        # Try user site-packages first, then system
        for loc_name in ['user', 'user_alt', 'system']:
            if locations.get(loc_name):
                print(f"   Trying {loc_name}: {locations[loc_name]}")
                installed_location = install_to_location(package_name, locations[loc_name])
                if installed_location:
                    break
    
    if not installed_location:
        print("❌ Could not install package to any location")
        print("   Try running with --local flag for local installation")
        return False
    
    # Create example notebook
    print("\n📓 Creating example notebook...")
    notebook_file = create_example_notebook()
    
    # Show usage instructions
    print("\n✅ Installation Complete!")
    print("=" * 50)
    print("📚 Usage in your projects:")
    print("   from bls_data import load_data, load_data_to_dataframe")
    print("   data = load_data(['All items', 'Food'], '2025-06')")
    print("   df = load_data_to_dataframe(['Energy', 'Shelter'], '2025-06')")
    
    print(f"\n📓 Example notebook created: {notebook_file}")
    print("   Open it in Jupyter to see usage examples")
    
    print(f"\n📦 Package installed to: {installed_location}")
    
    # Test the installation
    print("\n🧪 Testing installation...")
    try:
        # Add the installation directory to Python path for testing
        if str(installed_location.parent) not in sys.path:
            sys.path.insert(0, str(installed_location.parent))
        
        # Try importing
        import bls_data
        print("✅ Package import successful")
        
        # Test basic functionality
        if hasattr(bls_data, 'check_setup'):
            setup_ok = bls_data.check_setup()
            if setup_ok:
                print("✅ Package functionality test passed")
            else:
                print("⚠️  Package installed but data may not be available")
                print("   Run 'python run.py' to download data first")
        
    except Exception as e:
        print(f"⚠️  Package installed but import test failed: {e}")
        print("   You may need to restart Python or check PYTHONPATH")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)