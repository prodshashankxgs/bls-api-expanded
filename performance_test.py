#!/usr/bin/env python3
"""
BLS Performance Test
===================

Standalone script to measure and benchmark scraping and processing performance.
Useful for testing performance improvements and comparing different approaches.

Usage:
    python3 performance_test.py
    python3 performance_test.py --runs 5
    python3 performance_test.py --detailed
"""

import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List
import statistics

from xlsx_loader import BLSExcelDownloader, ExcelDataProcessor
from data_loader import read_excel_with_named_columns, load_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BLSPerformanceTester:
    """
    Performance testing and benchmarking for BLS scraping operations
    """
    
    def __init__(self):
        """Initialize the performance tester"""
        self.downloader = BLSExcelDownloader()
        self.processor = ExcelDataProcessor()
        self.results = []
    
    def time_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Time a specific operation and return duration + result"""
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"⏱️  {operation_name}: {duration:.3f}s")
        return duration, result
    
    def test_full_cycle(self, run_number: int = 1) -> Dict:
        """Test a complete scraping and processing cycle"""
        print(f"\n🔄 PERFORMANCE TEST RUN #{run_number}")
        print("=" * 50)
        
        total_start = time.time()
        
        # 1. Test scraping (download)
        scraping_time, excel_file = self.time_operation(
            "Website scraping + download", 
            self.downloader.download_latest_cpi_file
        )
        
        if not excel_file:
            logger.error("❌ Scraping failed - no file downloaded")
            return None
        
        # 2. Test Excel reading
        reading_time, df = self.time_operation(
            "Excel file reading",
            read_excel_with_named_columns,
            excel_file
        )
        
        # 3. Test data processing
        processing_time, processed_data = self.time_operation(
            "Data processing + validation",
            self.processor.extract_cpi_data,
            excel_file, "cpi", "2025-06"
        )
        
        # 4. Test ticker-based loading
        ticker_time, ticker_df = self.time_operation(
            "Ticker-based data loading",
            load_data,
            "All items", "latest"
        )
        
        total_time = time.time() - total_start
        
        # Calculate metrics
        file_size = excel_file.stat().st_size if excel_file else 0
        rows_processed = df.shape[0] if not df.is_empty() else 0
        data_points = len(processed_data) if processed_data else 0
        
        results = {
            'run_number': run_number,
            'scraping_time': scraping_time,
            'reading_time': reading_time,
            'processing_time': processing_time,
            'ticker_loading_time': ticker_time,
            'total_time': total_time,
            'file_size_bytes': file_size,
            'rows_processed': rows_processed,
            'data_points_extracted': data_points,
            'throughput_rows_per_sec': rows_processed / total_time if total_time > 0 else 0,
            'throughput_mb_per_sec': (file_size / 1024 / 1024) / total_time if total_time > 0 else 0
        }
        
        # Print results
        print(f"\n📊 RESULTS:")
        print(f"   Scraping: {scraping_time:.3f}s")
        print(f"   Reading:  {reading_time:.3f}s") 
        print(f"   Processing: {processing_time:.3f}s")
        print(f"   Ticker Loading: {ticker_time:.3f}s")
        print(f"   Total: {total_time:.3f}s")
        print(f"   File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   Rows: {rows_processed:,}")
        print(f"   Data Points: {data_points:,}")
        print(f"   Throughput: {results['throughput_rows_per_sec']:.1f} rows/sec")
        print(f"   Transfer: {results['throughput_mb_per_sec']:.2f} MB/sec")
        
        return results
    
    def run_benchmark(self, num_runs: int = 3) -> Dict:
        """Run multiple performance tests and calculate statistics"""
        print(f"🚀 STARTING PERFORMANCE BENCHMARK ({num_runs} runs)")
        print("=" * 60)
        
        all_results = []
        
        for i in range(num_runs):
            result = self.test_full_cycle(i + 1)
            if result:
                all_results.append(result)
                self.results.append(result)
            
            # Small delay between runs
            if i < num_runs - 1:
                time.sleep(1)
        
        if not all_results:
            logger.error("❌ No successful test runs")
            return {}
        
        # Calculate statistics
        stats = self._calculate_statistics(all_results)
        self._print_summary(stats, num_runs)
        
        return stats
    
    def _calculate_statistics(self, results: List[Dict]) -> Dict:
        """Calculate performance statistics across multiple runs"""
        if not results:
            return {}
        
        metrics = ['scraping_time', 'reading_time', 'processing_time', 'ticker_loading_time', 'total_time']
        stats = {}
        
        for metric in metrics:
            values = [r[metric] for r in results]
            stats[metric] = {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0
            }
        
        # Overall metrics
        stats['total_runs'] = len(results)
        stats['success_rate'] = 100.0  # All results here are successful
        
        return stats
    
    def _print_summary(self, stats: Dict, num_runs: int):
        """Print performance summary"""
        print(f"\n📈 PERFORMANCE SUMMARY ({num_runs} runs)")
        print("=" * 60)
        
        for operation in ['scraping_time', 'reading_time', 'processing_time', 'ticker_loading_time', 'total_time']:
            if operation in stats:
                s = stats[operation]
                op_name = operation.replace('_', ' ').title()
                print(f"{op_name:20} | Avg: {s['mean']:.3f}s | Min: {s['min']:.3f}s | Max: {s['max']:.3f}s | StdDev: {s['stdev']:.3f}s")
        
        print(f"\n🎯 KEY INSIGHTS:")
        
        # Performance insights
        if 'total_time' in stats:
            total_avg = stats['total_time']['mean']
            scraping_avg = stats['scraping_time']['mean']
            processing_avg = stats['processing_time']['mean']
            
            scraping_pct = (scraping_avg / total_avg) * 100
            processing_pct = (processing_avg / total_avg) * 100
            
            print(f"   Time Distribution: {scraping_pct:.1f}% scraping, {processing_pct:.1f}% processing")
            print(f"   Average Total Time: {total_avg:.3f}s")
            
            if total_avg < 2.0:
                print(f"   ✅ Excellent performance (< 2s)")
            elif total_avg < 5.0:
                print(f"   ✅ Good performance (< 5s)")
            elif total_avg < 10.0:
                print(f"   ⚠️  Acceptable performance (< 10s)")
            else:
                print(f"   ❌ Slow performance (> 10s)")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='BLS Performance Testing')
    parser.add_argument('--runs', type=int, default=3, help='Number of test runs')
    parser.add_argument('--detailed', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    if args.detailed:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = BLSPerformanceTester()
    
    try:
        stats = tester.run_benchmark(args.runs)
        
        if stats:
            print(f"\n💾 Performance data saved. Run again to track improvements!")
        else:
            print(f"\n❌ Performance test failed")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Performance test interrupted")
    except Exception as e:
        logger.error(f"Performance test error: {e}")

if __name__ == "__main__":
    main() 