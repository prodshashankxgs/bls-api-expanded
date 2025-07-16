#!/usr/bin/env python3
"""
BLS Data Processing Demo with Polars

This script demonstrates how to use Polars to process BLS economic data
from the FastAPI endpoints. It shows advanced data analysis capabilities
including trend analysis, correlation, and time series operations.
"""

import polars as pl
import httpx
import asyncio
from datetime import datetime, date
import json


class BLSDataProcessor:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def fetch_series_data(self, series_name: str, years: int = 3) -> pl.DataFrame:
        """Fetch BLS series data and convert to Polars DataFrame"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/data/{series_name}?years={years}")
            response.raise_for_status()
            data = response.json()
            
        # Convert to Polars DataFrame
        df = pl.DataFrame([
            {
                "date": point["date"],
                "value": point["value"],
                "year": point["year"],
                "period": point["period"],
                "month_change": point.get("month_change"),
                "year_change": point.get("year_change"),
                "trend": point.get("trend")
            }
            for point in data["data"]
        ])
        
        # Convert date column to proper datetime
        df = df.with_columns([
            pl.col("date").str.to_date().alias("date")
        ])
        
        # Add metadata
        df = df.with_columns([
            pl.lit(series_name).alias("series_name"),
            pl.lit(data["series_id"]).alias("series_id"),
            pl.lit(data["title"]).alias("title"),
            pl.lit(data["units"]).alias("units")
        ])
        
        return df.sort("date", descending=True)
    
    async def fetch_comparison_data(self, series1: str, series2: str, years: int = 2) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Fetch two series for comparison analysis"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/compare?series1={series1}&series2={series2}&years={years}")
            response.raise_for_status()
            data = response.json()
            
        # Convert both series to DataFrames
        df1 = pl.DataFrame([
            {
                "date": point["date"],
                "value": point["value"],
                "month_change": point.get("month_change"),
                "year_change": point.get("year_change"),
                "trend": point.get("trend")
            }
            for point in data["series1"]["data"]
        ]).with_columns([
            pl.col("date").str.to_date(),
            pl.lit(series1).alias("series_name")
        ])
        
        df2 = pl.DataFrame([
            {
                "date": point["date"],
                "value": point["value"],
                "month_change": point.get("month_change"),
                "year_change": point.get("year_change"),
                "trend": point.get("trend")
            }
            for point in data["series2"]["data"]
        ]).with_columns([
            pl.col("date").str.to_date(),
            pl.lit(series2).alias("series_name")
        ])
        
        return df1, df2
    
    def calculate_advanced_metrics(self, df: pl.DataFrame) -> pl.DataFrame:
        """Calculate advanced metrics using Polars expressions"""
        return df.with_columns([
            # Rolling averages
            pl.col("value").rolling_mean(window_size=3).alias("ma_3_month"),
            pl.col("value").rolling_mean(window_size=6).alias("ma_6_month"),
            pl.col("value").rolling_mean(window_size=12).alias("ma_12_month"),
            
            # Rolling standard deviation (volatility)
            pl.col("value").rolling_std(window_size=12).alias("volatility_12m"),
            
            # Z-score (standardized values)
            ((pl.col("value") - pl.col("value").mean()) / pl.col("value").std()).alias("z_score"),
            
            # Percentile rank
            pl.col("value").rank(method="ordinal").alias("rank"),
            
            # Custom trend strength
            (pl.col("month_change").abs() * 10).alias("trend_strength"),
            
            # Date components for seasonal analysis
            pl.col("date").dt.month().alias("month"),
            pl.col("date").dt.quarter().alias("quarter"),
            pl.col("date").dt.year().alias("data_year")
        ])
    
    def seasonal_analysis(self, df: pl.DataFrame) -> pl.DataFrame:
        """Perform seasonal analysis by month and quarter"""
        monthly_stats = df.group_by("month").agg([
            pl.col("value").mean().alias("avg_value"),
            pl.col("value").std().alias("std_value"),
            pl.col("value").count().alias("count")
        ]).sort("month")
        
        quarterly_stats = df.group_by("quarter").agg([
            pl.col("value").mean().alias("avg_value"),
            pl.col("value").std().alias("std_value"),
            pl.col("value").count().alias("count")
        ]).sort("quarter")
        
        return monthly_stats, quarterly_stats
    
    def correlation_analysis(self, df1: pl.DataFrame, df2: pl.DataFrame) -> dict:
        """Calculate correlation between two series"""
        # Join on date
        merged = df1.select(["date", "value"]).rename({"value": "series1_value"}).join(
            df2.select(["date", "value"]).rename({"value": "series2_value"}),
            on="date",
            how="inner"
        )
        
        if len(merged) == 0:
            return {"correlation": None, "message": "No overlapping dates found"}
        
        # Calculate Pearson correlation
        corr = merged.select([
            pl.corr("series1_value", "series2_value").alias("correlation")
        ]).item()
        
        return {
            "correlation": corr,
            "data_points": len(merged),
            "strength": "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.3 else "weak"
        }
    
    def trend_summary(self, df: pl.DataFrame) -> dict:
        """Generate trend summary statistics"""
        latest_6_months = df.head(6)
        
        summary = {
            "latest_value": df.select("value").head(1).item(),
            "latest_date": df.select("date").head(1).item().isoformat(),
            "6_month_avg": latest_6_months.select(pl.col("value").mean()).item(),
            "6_month_trend": latest_6_months.select(pl.col("month_change").mean()).item(),
            "volatility": df.head(12).select(pl.col("value").std()).item(),
            "trend_direction": "increasing" if latest_6_months.select(pl.col("month_change").mean()).item() > 0 else "decreasing"
        }
        
        return summary


async def demo_basic_analysis():
    """Demo basic data processing with Polars"""
    print("🔍 Basic BLS Data Analysis with Polars")
    print("=" * 50)
    
    processor = BLSDataProcessor()
    
    try:
        # Fetch unemployment data
        unemployment_df = await processor.fetch_series_data("unemployment", years=5)
        print(f"📊 Loaded {len(unemployment_df)} unemployment data points")
        print(unemployment_df.head())
        print()
        
        # Calculate advanced metrics
        enhanced_df = processor.calculate_advanced_metrics(unemployment_df)
        print("📈 Enhanced with advanced metrics:")
        print(enhanced_df.select(["date", "value", "ma_3_month", "ma_12_month", "z_score", "trend_strength"]).head())
        print()
        
        # Trend summary
        trend_summary = processor.trend_summary(enhanced_df)
        print("📋 Trend Summary:")
        for key, value in trend_summary.items():
            print(f"  {key}: {value}")
        print()
        
        # Seasonal analysis
        monthly_stats, quarterly_stats = processor.seasonal_analysis(enhanced_df)
        print("🗓️  Monthly Seasonal Patterns:")
        print(monthly_stats)
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the BLS API server is running: uvicorn app.main:app --reload")


async def demo_correlation_analysis():
    """Demo correlation analysis between economic indicators"""
    print("🔗 Economic Indicator Correlation Analysis")
    print("=" * 50)
    
    processor = BLSDataProcessor()
    
    try:
        # Compare unemployment vs inflation
        unemployment_df, inflation_df = await processor.fetch_comparison_data("unemployment", "inflation", years=3)
        
        print(f"📊 Unemployment data: {len(unemployment_df)} points")
        print(f"📊 Inflation data: {len(inflation_df)} points")
        print()
        
        # Correlation analysis
        correlation_results = processor.correlation_analysis(unemployment_df, inflation_df)
        print("🔍 Correlation Analysis:")
        print(f"  Correlation coefficient: {correlation_results.get('correlation', 'N/A'):.3f}")
        print(f"  Relationship strength: {correlation_results.get('strength', 'N/A')}")
        print(f"  Data points analyzed: {correlation_results.get('data_points', 0)}")
        print()
        
        # Combined analysis
        combined_df = unemployment_df.select(["date", "value", "trend"]).rename({"value": "unemployment"}).join(
            inflation_df.select(["date", "value", "trend"]).rename({"value": "inflation"}),
            on="date",
            how="inner"
        )
        
        print("📈 Combined Economic Indicators (Latest 10 months):")
        print(combined_df.head(10))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the BLS API server is running: uvicorn app.main:app --reload")


async def demo_multi_series_dashboard():
    """Demo multi-series economic dashboard with Polars"""
    print("📊 Economic Dashboard with Polars")
    print("=" * 50)
    
    processor = BLSDataProcessor()
    
    series_names = ["unemployment", "inflation", "jobs", "wages"]
    all_series = {}
    
    try:
        # Fetch all series
        for series in series_names:
            try:
                df = await processor.fetch_series_data(series, years=2)
                all_series[series] = df
                print(f"✅ Loaded {series}: {len(df)} data points")
            except Exception as e:
                print(f"❌ Failed to load {series}: {e}")
        
        print()
        
        # Create combined dashboard view
        dashboard_data = []
        for series_name, df in all_series.items():
            if len(df) > 0:
                latest = df.head(1)
                summary = processor.trend_summary(df)
                dashboard_data.append({
                    "indicator": series_name,
                    "latest_value": summary["latest_value"],
                    "latest_date": summary["latest_date"],
                    "6_month_trend": summary["6_month_trend"],
                    "trend_direction": summary["trend_direction"],
                    "volatility": summary["volatility"]
                })
        
        # Convert to Polars DataFrame for advanced analysis
        dashboard_df = pl.DataFrame(dashboard_data)
        print("📋 Economic Dashboard Summary:")
        print(dashboard_df)
        print()
        
        # Find most volatile indicators
        most_volatile = dashboard_df.sort("volatility", descending=True).head(1)
        print("⚡ Most Volatile Indicator:")
        print(most_volatile)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the BLS API server is running: uvicorn app.main:app --reload")


async def main():
    """Run all demo functions"""
    print("🚀 BLS Data Processing Demo with Polars")
    print("🔧 Make sure to start the API server first:")
    print("   uvicorn app.main:app --reload")
    print()
    
    await demo_basic_analysis()
    print("\n" + "="*70 + "\n")
    
    await demo_correlation_analysis()
    print("\n" + "="*70 + "\n")
    
    await demo_multi_series_dashboard()
    
    print("\n🎉 Demo complete! Polars enables powerful data analysis:")
    print("  ✓ Fast data loading and processing")
    print("  ✓ Advanced statistical calculations")
    print("  ✓ Seasonal and trend analysis") 
    print("  ✓ Multi-series correlation analysis")
    print("  ✓ Economic dashboard creation")


if __name__ == "__main__":
    asyncio.run(main())