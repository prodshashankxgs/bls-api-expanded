import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging


class FredDataPipeline:
    """Pipeline to process and validate FRED data items"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_item(self, item, spider):
        """Process and validate FRED data items"""
        # Validate required fields
        required_fields = ['series_id', 'data_points']
        for field in required_fields:
            if not item.get(field):
                raise DropItem(f"Missing required field: {field}")
        
        # Provide default title if missing
        if not item.get('title'):
            item['title'] = item.get('series_id', 'Unknown Series')
        
        # Sort data points by date
        if item.get('data_points'):
            item['data_points'] = sorted(
                item['data_points'], 
                key=lambda x: x.get('date', '')
            )
        
        # Add processing metadata
        item['processed_at'] = datetime.now().isoformat()
        item['data_count'] = len(item.get('data_points', []))
        
        self.logger.info(f"Processed {item['series_id']} with {item['data_count']} data points")
        return item


class CachePipeline:
    """Pipeline to cache scraped data"""
    
    def __init__(self, cache_dir='cached_data'):
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    @classmethod
    def from_crawler(cls, crawler):
        cache_dir = crawler.settings.get('CACHE_DIR', 'cached_data')
        return cls(cache_dir)
    
    def process_item(self, item, spider):
        """Cache item data to filesystem"""
        series_id = item.get('series_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create filename
        filename = f"{series_id}_{timestamp}.json"
        filepath = os.path.join(self.cache_dir, filename)
        
        # Save to JSON file
        try:
            with open(filepath, 'w') as f:
                json.dump(dict(item), f, indent=2, default=str)
            
            self.logger.info(f"Cached {series_id} to {filepath}")
            
            # Also save as latest
            latest_filepath = os.path.join(self.cache_dir, f"{series_id}_latest.json")
            with open(latest_filepath, 'w') as f:
                json.dump(dict(item), f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to cache {series_id}: {e}")
        
        return item


class DatabasePipeline:
    """Pipeline to store data in SQLite database"""
    
    def __init__(self, db_path='fred_data.db'):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_crawler(cls, crawler):
        db_path = crawler.settings.get('DATABASE_PATH', 'fred_data.db')
        return cls(db_path)
    
    def open_spider(self, spider):
        """Initialize database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.create_tables()
    
    def close_spider(self, spider):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def create_tables(self):
        """Create database tables"""
        if self.connection is None:
            raise RuntimeError("Database connection not initialized")
            
        cursor = self.connection.cursor()
        
        # Series metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS series_metadata (
                series_id TEXT PRIMARY KEY,
                ticker TEXT,
                title TEXT,
                units TEXT,
                frequency TEXT,
                seasonal_adjustment TEXT,
                last_updated TEXT,
                source_url TEXT,
                scraped_at TEXT,
                processed_at TEXT
            )
        ''')
        
        # Data points table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_id TEXT,
                date TEXT,
                value REAL,
                period TEXT,
                year INTEGER,
                month INTEGER,
                FOREIGN KEY (series_id) REFERENCES series_metadata (series_id),
                UNIQUE(series_id, date)
            )
        ''')
        
        self.connection.commit()
    
    def process_item(self, item, spider):
        """Store item in database"""
        if self.connection is None:
            raise RuntimeError("Database connection not initialized")
            
        cursor = self.connection.cursor()
        
        try:
            # Insert or update series metadata
            cursor.execute('''
                INSERT OR REPLACE INTO series_metadata 
                (series_id, ticker, title, units, frequency, seasonal_adjustment, 
                 last_updated, source_url, scraped_at, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('series_id'),
                item.get('ticker'),
                item.get('title'),
                item.get('units'),
                item.get('frequency'),
                item.get('seasonal_adjustment'),
                item.get('last_updated'),
                item.get('source_url'),
                item.get('scraped_at'),
                item.get('processed_at')
            ))
            
            # Insert data points
            for point in item.get('data_points', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO data_points 
                    (series_id, date, value, period, year, month)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('series_id'),
                    point.get('date'),
                    point.get('value'),
                    point.get('period'),
                    point.get('year'),
                    point.get('month')
                ))
            
            self.connection.commit()
            self.logger.info(f"Stored {item['series_id']} in database")
            
        except Exception as e:
            self.logger.error(f"Database error for {item.get('series_id')}: {e}")
            self.connection.rollback()
        
        return item


class DropItem(Exception):
    """Exception to drop items from pipeline"""
    pass 