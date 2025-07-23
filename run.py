#!/usr/bin/env python3
"""
bls economic data api - simple runner
one-command startup for the complete bls scraper api
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """check if all required packages are installed"""
    # map package names to their import names
    packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn', 
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'lxml': 'lxml',
        'python-dotenv': 'dotenv'
    }
    missing = []
    
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"missing packages: {', '.join(missing)}")
        print("run: pip install -r requirements.txt")
        return False
    
    print("all dependencies installed")
    return True

def setup_environment():
    """set up environment and create directories"""
    # create necessary directories
    Path('data_cache').mkdir(exist_ok=True)
    
    # set default environment variables
    defaults = {
        'HOST': '0.0.0.0',
        'PORT': '8000',
        'WORKERS': '1',
        'CACHE_TTL': '3600',
        'MAX_RESULTS': '1000'
    }
    
    for key, value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = value
    
    print(f"server will run on: http://{os.getenv('HOST')}:{os.getenv('PORT')}")
    print(f"documentation: http://{os.getenv('HOST')}:{os.getenv('PORT')}/docs")

def main():
    """main entry point"""
    print("bls economic data api")
    print("=" * 40)
    
    # check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # setup environment
    setup_environment()
    
    print("starting production server...")
    print("press ctrl+c to stop")
    print("=" * 40)
    
    try:
        # import and run the api
        from bls_api import main as start_server
        start_server()
    except KeyboardInterrupt:
        print("\nserver stopped")
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()