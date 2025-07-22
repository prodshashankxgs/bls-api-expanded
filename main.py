#!/usr/bin/env python3
"""
BLS Economic Data Scraper - Main Entry Point
Simple, fast, and reliable economic data scraping

Usage:
    python main.py                    # Run interactive demo
    python main.py --test             # Run performance tests
    python main.py --clear-cache      # Clear data cache
"""

import sys
import argparse
from bls_scraper import load_data, run_performance_test, clear_cache, get_available_indicators

def interactive_demo():
    """Run interactive demonstration"""
    print("🌐 BLS Economic Data Scraper - Interactive Demo")
    print("="*60)
    
    # Show available indicators
    indicators = get_available_indicators()
    print("📊 Available indicators:")
    for key, value in indicators.items():
        print(f"   {key} -> {value}")
    
    print("\n💡 Example usage:")
    print("   load_data('cpi', '2022-2024')")
    print("   load_data('unemployment', 'last 3 years')")
    
    # Interactive examples
    examples = [
        ('cpi', '2023-2024', 'CPI All Items'),
        ('cpi_core', '2023', 'Core CPI (without food/energy)'),
        ('unemployment', '2022-2024', 'Unemployment Rate')
    ]
    
    for ticker, date_range, description in examples:
        print(f"\n🔸 Loading {description}...")
        print(f"   Command: load_data('{ticker}', '{date_range}')")
        
        try:
            data = load_data(ticker, date_range)
            if data:
                print(f"   ✅ Success: {len(data)} data points")
                latest = data[0]
                print(f"   📊 Latest: {latest['value']} ({latest['date']})")
                print(f"   🔄 Source: {latest['source']}")
            else:
                print("   ❌ No data retrieved")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='BLS Economic Data Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Interactive demo
    python main.py --test             # Performance tests  
    python main.py --clear-cache      # Clear cache
    
In Python code:
    from bls_scraper import load_data
    cpi_data = load_data('cpi', '2022-2024')
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Run performance tests')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear the data cache')
    
    args = parser.parse_args()
    
    if args.clear_cache:
        print("🗑️  Clearing cache...")
        clear_cache()
        return
    
    if args.test:
        print("🧪 Running performance tests...")
        success = run_performance_test()
        sys.exit(0 if success else 1)
    
    # Default: interactive demo
    interactive_demo()
    
    print("\n" + "="*60)
    print("✅ BLS Scraper ready for use!")
    print("📖 Import: from bls_scraper import load_data")
    print("🚀 Usage: load_data('cpi', '2020-2024')")

if __name__ == "__main__":
    main()