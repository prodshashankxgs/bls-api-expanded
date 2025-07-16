#!/usr/bin/env python3
"""
Sample BLS Data Generator

Creates sample economic data in the same format as the BLS API
for testing the Polars demo when the API server is not running.
"""

import json
import polars as pl
from datetime import datetime, date, timedelta
import random
import math


def generate_sample_unemployment_data(years: int = 3) -> dict:
    """Generate realistic unemployment rate data"""
    base_rate = 4.0  # Base unemployment rate
    data_points = []
    
    start_date = datetime.now() - timedelta(days=years * 365)
    current_date = start_date
    
    # Add some trend and seasonality
    trend = -0.1  # Slight downward trend
    seasonal_amplitude = 0.3
    
    while current_date <= datetime.now():
        # Calculate seasonal component (higher in winter)
        month = current_date.month
        seasonal = seasonal_amplitude * math.sin(2 * math.pi * (month - 3) / 12)
        
        # Add some random noise
        noise = random.uniform(-0.2, 0.2)
        
        # Calculate value
        months_elapsed = (current_date - start_date).days / 30.44
        value = base_rate + trend * months_elapsed / 12 + seasonal + noise
        value = max(2.0, min(8.0, value))  # Keep within realistic bounds
        
        # Calculate changes
        month_change = None
        year_change = None
        if data_points:
            prev_value = data_points[-1]["value"]
            month_change = ((value - prev_value) / prev_value) * 100
            
        if len(data_points) >= 12:
            year_ago_value = data_points[-12]["value"]
            year_change = ((value - year_ago_value) / year_ago_value) * 100
        
        # Determine trend
        trend_label = "stable"
        if month_change:
            if month_change > 0.1:
                trend_label = "increasing"
            elif month_change < -0.1:
                trend_label = "decreasing"
        
        data_point = {
            "date": current_date.strftime("%Y-%m-%d"),
            "value": round(value, 1),
            "period": f"M{current_date.month:02d}",
            "year": current_date.year,
            "month_change": round(month_change, 2) if month_change else None,
            "year_change": round(year_change, 2) if year_change else None,
            "trend": trend_label
        }
        
        data_points.append(data_point)
        current_date += timedelta(days=30)  # Roughly monthly
    
    return {
        "series_name": "unemployment",
        "series_id": "LNS14000000",
        "title": "Unemployment Rate",
        "units": "Percent",
        "data": list(reversed(data_points)),  # BLS returns newest first
        "last_updated": date.today().isoformat(),
        "total_points": len(data_points),
        "fetch_time_seconds": 0.001,
        "cached": False
    }


def generate_sample_inflation_data(years: int = 3) -> dict:
    """Generate realistic CPI inflation data"""
    base_cpi = 280.0  # Base CPI index
    data_points = []
    
    start_date = datetime.now() - timedelta(days=years * 365)
    current_date = start_date
    
    # Inflation trend
    annual_inflation = 0.025  # 2.5% annual inflation
    
    while current_date <= datetime.now():
        months_elapsed = (current_date - start_date).days / 30.44
        
        # Calculate value with some volatility
        growth_factor = (1 + annual_inflation) ** (months_elapsed / 12)
        noise = random.uniform(-0.02, 0.02)
        value = base_cpi * growth_factor * (1 + noise)
        
        # Calculate changes
        month_change = None
        year_change = None
        if data_points:
            prev_value = data_points[-1]["value"]
            month_change = ((value - prev_value) / prev_value) * 100
            
        if len(data_points) >= 12:
            year_ago_value = data_points[-12]["value"]
            year_change = ((value - year_ago_value) / year_ago_value) * 100
        
        trend_label = "stable"
        if month_change:
            if month_change > 0.2:
                trend_label = "increasing"
            elif month_change < -0.2:
                trend_label = "decreasing"
        
        data_point = {
            "date": current_date.strftime("%Y-%m-%d"),
            "value": round(value, 1),
            "period": f"M{current_date.month:02d}",
            "year": current_date.year,
            "month_change": round(month_change, 2) if month_change else None,
            "year_change": round(year_change, 2) if year_change else None,
            "trend": trend_label
        }
        
        data_points.append(data_point)
        current_date += timedelta(days=30)
    
    return {
        "series_name": "inflation",
        "series_id": "CUUR0000SA0",
        "title": "Consumer Price Index - All Urban Consumers",
        "units": "Index 1982-84=100",
        "data": list(reversed(data_points)),
        "last_updated": date.today().isoformat(),
        "total_points": len(data_points),
        "fetch_time_seconds": 0.001,
        "cached": False
    }


def generate_sample_jobs_data(years: int = 3) -> dict:
    """Generate realistic employment data"""
    base_jobs = 150000  # Base employment in thousands
    data_points = []
    
    start_date = datetime.now() - timedelta(days=years * 365)
    current_date = start_date
    
    growth_rate = 0.015  # 1.5% annual job growth
    
    while current_date <= datetime.now():
        months_elapsed = (current_date - start_date).days / 30.44
        
        # Add seasonality (retail hiring in winter holidays)
        seasonal = 200 * math.sin(2 * math.pi * (current_date.month - 11) / 12)
        noise = random.uniform(-500, 500)
        
        growth_factor = (1 + growth_rate) ** (months_elapsed / 12)
        value = base_jobs * growth_factor + seasonal + noise
        
        month_change = None
        year_change = None
        if data_points:
            prev_value = data_points[-1]["value"]
            month_change = ((value - prev_value) / prev_value) * 100
            
        if len(data_points) >= 12:
            year_ago_value = data_points[-12]["value"]
            year_change = ((value - year_ago_value) / year_ago_value) * 100
        
        trend_label = "stable"
        if month_change:
            if month_change > 0.1:
                trend_label = "increasing"
            elif month_change < -0.1:
                trend_label = "decreasing"
        
        data_point = {
            "date": current_date.strftime("%Y-%m-%d"),
            "value": round(value, 0),
            "period": f"M{current_date.month:02d}",
            "year": current_date.year,
            "month_change": round(month_change, 2) if month_change else None,
            "year_change": round(year_change, 2) if year_change else None,
            "trend": trend_label
        }
        
        data_points.append(data_point)
        current_date += timedelta(days=30)
    
    return {
        "series_name": "jobs",
        "series_id": "CES0000000001",
        "title": "Total Nonfarm Employment",
        "units": "Thousands of Persons",
        "data": list(reversed(data_points)),
        "last_updated": date.today().isoformat(),
        "total_points": len(data_points),
        "fetch_time_seconds": 0.001,
        "cached": False
    }


def save_sample_data():
    """Generate and save sample data files"""
    
    series_generators = {
        "unemployment": generate_sample_unemployment_data,
        "inflation": generate_sample_inflation_data,
        "jobs": generate_sample_jobs_data
    }
    
    print("🔄 Generating sample BLS data...")
    
    for series_name, generator in series_generators.items():
        data = generator(years=3)
        filename = f"sample_{series_name}_data.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Generated {filename} with {data['total_points']} data points")
    
    print("📊 Sample data files created successfully!")


if __name__ == "__main__":
    save_sample_data()