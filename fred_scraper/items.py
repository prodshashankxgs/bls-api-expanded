import scrapy
from datetime import date
from typing import Optional


class FredDataItem(scrapy.Item):
    """Item for FRED economic data points"""
    series_id = scrapy.Field()
    ticker = scrapy.Field()
    title = scrapy.Field()
    units = scrapy.Field()
    frequency = scrapy.Field()
    seasonal_adjustment = scrapy.Field()
    last_updated = scrapy.Field()
    data_points = scrapy.Field()  # List of data points
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()
    processed_at = scrapy.Field()
    data_count = scrapy.Field()


class FredDataPoint(scrapy.Item):
    """Individual data point from FRED series"""
    date = scrapy.Field()
    value = scrapy.Field()
    period = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()


class FredSeriesInfo(scrapy.Item):
    """Metadata about FRED series"""
    series_id = scrapy.Field()
    title = scrapy.Field()
    units = scrapy.Field()
    frequency = scrapy.Field()
    seasonal_adjustment = scrapy.Field()
    notes = scrapy.Field()
    source = scrapy.Field()
    release = scrapy.Field()
    last_updated = scrapy.Field()
    popularity = scrapy.Field()
    group_popularity = scrapy.Field() 