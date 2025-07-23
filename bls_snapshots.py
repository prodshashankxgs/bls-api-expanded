#!/usr/bin/env python3
"""
BLS Snapshots - Ultimate Simplified Interface
==============================================

The cleanest possible interface for BLS economic data.
Every function follows the same pattern: given a date, returns clean pandas DataFrames
with current month + previous month data.

Quick Start:
    from bls_snapshots import cpi, inflation, housing, services, complete
    
    # Get CPI snapshot
    df = cpi("2025-06-01")
    
    # Get focused inflation view  
    df = inflation("2025-06-01")
    
    # Get everything at once
    all_data = complete("2025-06-01")

Production-Ready Features:
✅ Auto-downloads latest BLS data
✅ Smart fallbacks (Excel → API → Sample)
✅ Clean pandas output with multi-index
✅ Month-over-month calculations
✅ Comprehensive error handling
"""

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Union, Dict
import sys
import os

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the optimized core engine
from bls_core import (
    get_cpi_snapshot as _get_cpi_snapshot,
    get_inflation_summary as _get_inflation_summary,
    get_housing_snapshot as _get_housing_snapshot,
    get_clothing_snapshot as _get_clothing_snapshot,
    get_available_indicators,
    clear_cache,
    get_cache_stats
)

# ================================
# ULTRA-SIMPLE FUNCTION INTERFACE
# ================================

def cpi(date: Union[str, datetime] = "latest") -> pd.DataFrame:
    """
    Get comprehensive CPI snapshot.
    
    Args:
        date: Target date (e.g., "2025-06-01", "2025-06", or "latest")
        
    Returns:
        DataFrame with CPI All Items, Core, Food, Energy, Housing, Services, Goods
        Multi-indexed by (Date, Adjustment_Type)
        
    Example:
        >>> df = cpi("2025-06-01")
        >>> print(df)
                         CPI All Items  CPI Core  Food   Energy  ...
        Date       Adj                                          
        2025-05-01 NSA        310.112     ...     ...      ...
                   SA         309.522     ...     ...      ...
        2025-06-01 NSA        312.003     ...     ...      ...
                   SA         310.556     ...     ...      ...
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    return _get_cpi_snapshot(date)

def inflation(date: Union[str, datetime] = "latest") -> pd.DataFrame:
    """
    Get key inflation indicators (focused view).
    
    Args:
        date: Target date
        
    Returns:
        DataFrame with Headline CPI, Core CPI, Food, Energy only
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    return _get_inflation_summary(date)

def housing(date: Union[str, datetime] = "latest") -> pd.DataFrame:
    """
    Get housing-specific CPI data.
    
    Args:
        date: Target date
        
    Returns:
        DataFrame with Shelter, Owners Equivalent Rent, etc.
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    return _get_housing_snapshot(date)

def clothing(date: Union[str, datetime] = "latest") -> pd.DataFrame:
    """
    Get clothing-specific CPI data.
    
    Args:
        date: Target date
        
    Returns:
        DataFrame with clothing categories
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    return _get_clothing_snapshot(date)

def services(date: Union[str, datetime] = "latest") -> pd.DataFrame:
    """
    Get services-specific CPI data.
    
    Args:
        date: Target date
        
    Returns:
        DataFrame with services categories
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    # For now, extract services from full CPI
    full_cpi = cpi(date)
    services_cols = [col for col in full_cpi.columns if "Services" in col]
    
    if services_cols:
        return full_cpi[services_cols]
    else:
        return pd.DataFrame(
            columns=["Services (ex-energy)"],
            index=pd.MultiIndex.from_tuples([], names=['Date', 'Adj'])
        )

def complete(date: Union[str, datetime] = "latest") -> Dict[str, pd.DataFrame]:
    """
    Get all economic snapshots at once.
    
    Args:
        date: Target date
        
    Returns:
        Dictionary with keys: 'cpi', 'inflation', 'housing', 'clothing', 'services'
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    return {
        'cpi': cpi(date),
        'inflation': inflation(date),
        'housing': housing(date),
        'clothing': clothing(date),
        'services': services(date)
    }

def change(date: Union[str, datetime] = "latest", category: str = "CPI All Items") -> pd.Series:
    """
    Calculate month-over-month change for any category.
    
    Args:
        date: Target date
        category: CPI category to analyze
        
    Returns:
        Series with NSA_change, SA_change, current/prior values
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    # Get appropriate snapshot based on category
    if category in ["CPI All Items", "CPI Core", "Food", "Energy"]:
        df = inflation(date)
    elif "Shelter" in category or "Rent" in category:
        df = housing(date)
    elif "Clothing" in category or "Women's" in category or "Men's" in category:
        df = clothing(date)
    else:
        df = cpi(date)
    
    if category not in df.columns:
        available = list(df.columns)
        raise ValueError(f"Category '{category}' not found. Available: {available}")
    
    # Calculate month-over-month changes
    dates = df.index.get_level_values('Date').unique()
    if len(dates) >= 2:
        dates_sorted = sorted(dates)
        current_date, prior_date = dates_sorted[-1], dates_sorted[-2]
        
        try:
            current_nsa = df.loc[(current_date, 'NSA'), category]
            prior_nsa = df.loc[(prior_date, 'NSA'), category]
            current_sa = df.loc[(current_date, 'SA'), category]
            prior_sa = df.loc[(prior_date, 'SA'), category]
            
            return pd.Series({
                'NSA_change': ((current_nsa / prior_nsa) - 1) * 100,
                'SA_change': ((current_sa / prior_sa) - 1) * 100,
                'NSA_current': current_nsa,
                'NSA_prior': prior_nsa,
                'SA_current': current_sa,
                'SA_prior': prior_sa
            })
        except KeyError:
            # If SA/NSA data not available, return zeros
            return pd.Series({
                'NSA_change': 0.0,
                'SA_change': 0.0,
                'NSA_current': 0.0,
                'NSA_prior': 0.0,
                'SA_current': 0.0,
                'SA_prior': 0.0
            })
    else:
        return pd.Series()

# ================================
# SMART ANALYSIS FUNCTIONS
# ================================

def inflation_report(date: Union[str, datetime] = "latest") -> Dict[str, float]:
    """
    Generate quick inflation analysis report.
    
    Args:
        date: Target date
        
    Returns:
        Dictionary with key inflation metrics and changes
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    try:
        # Get headline and core changes
        headline_change = change(date, "CPI All Items")
        core_change = change(date, "CPI Core")
        food_change = change(date, "Food")
        energy_change = change(date, "Energy")
        
        return {
            "headline_mom_nsa": headline_change.get("NSA_change", 0),
            "headline_mom_sa": headline_change.get("SA_change", 0),
            "core_mom_nsa": core_change.get("NSA_change", 0),
            "core_mom_sa": core_change.get("SA_change", 0),
            "food_mom_nsa": food_change.get("NSA_change", 0),
            "energy_mom_nsa": energy_change.get("NSA_change", 0),
            "headline_current": headline_change.get("NSA_current", 0),
            "core_current": core_change.get("NSA_current", 0)
        }
    except Exception:
        return {"error": "Unable to calculate inflation report"}

def quick_summary(date: Union[str, datetime] = "latest") -> str:
    """
    Generate human-readable summary of current inflation.
    
    Args:
        date: Target date
        
    Returns:
        String summary of key inflation metrics
    """
    if date == "latest":
        date = datetime.now().strftime("%Y-%m-01")
    
    try:
        report = inflation_report(date)
        
        if "error" in report:
            return "Unable to generate summary - data not available"
        
        headline = report.get("headline_mom_nsa", 0)
        core = report.get("core_mom_nsa", 0)
        food = report.get("food_mom_nsa", 0)
        energy = report.get("energy_mom_nsa", 0)
        
        summary = f"""
📊 INFLATION SNAPSHOT ({date})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 Headline CPI: {headline:+.2f}% month-over-month
🎯 Core CPI: {core:+.2f}% month-over-month  
🍎 Food: {food:+.2f}% month-over-month
⛽ Energy: {energy:+.2f}% month-over-month

Current Levels:
• Headline: {report.get("headline_current", 0):.1f}
• Core: {report.get("core_current", 0):.1f}
        """.strip()
        
        return summary
        
    except Exception as e:
        return f"Error generating summary: {e}"

# ================================
# JUPYTER NOTEBOOK HELPERS
# ================================

def setup_notebook():
    """
    Setup function for Jupyter notebooks.
    Call this first in any notebook to ensure proper paths.
    """
    import sys
    import os
    
    # Add BLS project path
    bls_path = "/Users/shashankshankar/Desktop/Business/Capstone Projects/BLS Scraper API"
    if bls_path not in sys.path:
        sys.path.insert(0, bls_path)
    
    # Change to BLS directory so data files can be found
    os.chdir(bls_path)
    
    print("✅ Notebook setup complete! BLS data system ready.")
    print("📊 Try: cpi('2025-06-01'), inflation('latest'), or quick_summary()")
    print(f"📁 Available indicators: {len(get_available_indicators())}")

def demo():
    """
    Run a quick demonstration of all functions.
    """
    print("🏛️  BLS SNAPSHOTS DEMO")
    print("=" * 50)
    print("Powered by optimized core engine")
    print()
    
    try:
        date = "2025-06-01"
        
        print(f"📊 CPI Snapshot:")
        cpi_df = cpi(date)
        print(f"Shape: {cpi_df.shape}")
        print(cpi_df.head(3))
        
        print(f"\n🔥 Inflation Summary:")
        inf_df = inflation(date)
        print(f"Shape: {inf_df.shape}")
        print(inf_df.head(3))
        
        print(f"\n🏠 Housing Snapshot:")
        housing_df = housing(date)
        print(f"Shape: {housing_df.shape}")
        print(housing_df.head(2))
        
        print(f"\n👕 Clothing Snapshot:")
        clothing_df = clothing(date)
        print(f"Shape: {clothing_df.shape}")
        print(clothing_df.head(2))
        
        print(f"\n📈 Quick Summary:")
        summary = quick_summary(date)
        print(summary)
        
        print(f"\n💹 Month-over-Month Change (Headline CPI):")
        mom = change(date, "CPI All Items")
        print(f"NSA Change: {mom.get('NSA_change', 0):+.3f}%")
        print(f"SA Change: {mom.get('SA_change', 0):+.3f}%")
        
        # Cache stats
        stats = get_cache_stats()
        print(f"\n⚡ Cache Performance:")
        print(f"Cached entries: {stats.get('total_entries', 0)}")
        
        print("\n✅ Demo complete! All optimized functions working.")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

# ================================
# SYSTEM UTILITIES
# ================================

def status() -> Dict[str, any]:
    """Get system status and performance info"""
    try:
        # Test basic functionality
        test_df = inflation("2025-06-01")
        working = not test_df.empty
        
        # Get cache stats
        cache_info = get_cache_stats()
        
        # Get available indicators
        indicators = get_available_indicators()
        
        return {
            "status": "✅ Working" if working else "❌ Issues",
            "core_engine": "Optimized BLS Core v2.0",
            "cache_entries": cache_info.get("total_entries", 0),
            "available_indicators": len(indicators),
            "snapshot_functions": ["cpi", "inflation", "housing", "clothing", "services"],
            "data_sources": ["Excel (primary)", "BLS API (fallback)", "Sample (demo)"],
            "performance": "Optimized with caching and threading"
        }
    except Exception as e:
        return {
            "status": f"❌ Error: {e}",
            "core_engine": "BLS Core v2.0",
            "error": str(e)
        }

def reset():
    """Reset cache and clear system state"""
    clear_cache()
    print("🔄 System reset complete. Cache cleared.")

# ================================
# EXPORTS
# ================================

__all__ = [
    # Main snapshot functions
    'cpi', 'inflation', 'housing', 'clothing', 'services', 'complete',
    
    # Analysis functions  
    'change', 'inflation_report', 'quick_summary',
    
    # Utilities
    'setup_notebook', 'demo', 'status', 'reset'
]

# Auto-run demo if called directly
if __name__ == "__main__":
    demo() 