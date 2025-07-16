import scrapy
import json
import re
from datetime import datetime, date
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs
from ..items import FredDataItem, FredDataPoint, FredSeriesInfo


class FredSpider(scrapy.Spider):
    """Spider for scraping FRED (Federal Reserve Economic Data) website"""
    
    name = 'fred'
    allowed_domains = ['fred.stlouisfed.org']
    start_urls = ['https://fred.stlouisfed.org/']
    
    def __init__(self, series_id=None, ticker=None, *args, **kwargs):
        super(FredSpider, self).__init__(*args, **kwargs)
        self.series_id = series_id
        self.ticker = ticker
        
        # Popular economic series mapping
        self.ticker_to_series = {
            'GDP': 'GDP',
            'UNRATE': 'UNRATE',
            'CPIAUCSL': 'CPIAUCSL',
            'FEDFUNDS': 'FEDFUNDS',
            'DFF': 'DFF',
            'PAYEMS': 'PAYEMS',
            'HOUST': 'HOUST',
            'DEXUSEU': 'DEXUSEU',
            'DEXJPUS': 'DEXJPUS',
            'DCOILWTICO': 'DCOILWTICO',
            'GOLDAMGBD228NLBM': 'GOLDAMGBD228NLBM',
        }
    
    def start_requests(self):
        """Generate initial requests based on series_id or ticker"""
        if self.series_id:
            url = f"https://fred.stlouisfed.org/series/{self.series_id}"
            yield scrapy.Request(url, callback=self.parse_series_page)
        elif self.ticker:
            series_id = self.ticker_to_series.get(self.ticker, self.ticker)
            url = f"https://fred.stlouisfed.org/series/{series_id}"
            yield scrapy.Request(url, callback=self.parse_series_page)
        else:
            # Default: scrape popular series
            for ticker, series_id in self.ticker_to_series.items():
                url = f"https://fred.stlouisfed.org/series/{series_id}"
                yield scrapy.Request(url, callback=self.parse_series_page)
    
    def parse_series_page(self, response):
        """Parse a FRED series page to extract metadata and data"""
        series_id = self.extract_series_id_from_url(response.url)
        
        # Extract series metadata
        series_info = self.extract_series_info(response, series_id)
        
        # Extract data points from the page
        data_points = self.extract_data_points(response)
        
        # Check if we need to get more data via download
        download_url = self.get_download_url(response, series_id)
        if download_url:
            yield scrapy.Request(
                download_url,
                callback=self.parse_csv_data,
                meta={'series_info': series_info, 'series_id': series_id}
            )
        else:
            # Use data from the page
            yield FredDataItem(
                series_id=series_id,
                ticker=series_info.get('ticker', series_id),
                title=series_info.get('title', ''),
                units=series_info.get('units', ''),
                frequency=series_info.get('frequency', ''),
                seasonal_adjustment=series_info.get('seasonal_adjustment', ''),
                last_updated=series_info.get('last_updated', ''),
                data_points=data_points,
                source_url=response.url,
                scraped_at=datetime.now().isoformat()
            )
    
    def parse_csv_data(self, response):
        """Parse CSV data from FRED download"""
        series_info = response.meta['series_info']
        series_id = response.meta['series_id']
        
        data_points = []
        lines = response.text.strip().split('\n')
        
        # Skip header if present
        start_idx = 1 if lines[0].startswith('DATE') else 0
        
        for line in lines[start_idx:]:
            if not line.strip():
                continue
                
            parts = line.split(',')
            if len(parts) >= 2:
                date_str = parts[0].strip()
                value_str = parts[1].strip()
                
                if value_str and value_str != '.' and value_str != 'NA':
                    try:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        value = float(value_str)
                        
                        data_point = FredDataPoint(
                            date=parsed_date.isoformat(),
                            value=value,
                            period=f"{parsed_date.year}-{parsed_date.month:02d}",
                            year=parsed_date.year,
                            month=parsed_date.month
                        )
                        data_points.append(dict(data_point))
                    except (ValueError, TypeError):
                        continue
        
        yield FredDataItem(
            series_id=series_id,
            ticker=series_info.get('ticker', series_id),
            title=series_info.get('title', ''),
            units=series_info.get('units', ''),
            frequency=series_info.get('frequency', ''),
            seasonal_adjustment=series_info.get('seasonal_adjustment', ''),
            last_updated=series_info.get('last_updated', ''),
            data_points=data_points,
            source_url=response.url,
            scraped_at=datetime.now().isoformat()
        )
    
    def extract_series_id_from_url(self, url: str) -> str:
        """Extract series ID from FRED URL"""
        path = urlparse(url).path
        if '/series/' in path:
            return path.split('/series/')[-1].split('/')[0]
        return ''
    
    def extract_series_info(self, response, series_id: str) -> Dict:
        """Extract series metadata from the page"""
        info = {'ticker': series_id}
        
        # Extract title
        title_selector = 'h1.series-title::text'
        title = response.css(title_selector).get()
        if title:
            info['title'] = title.strip()
        
        # Extract units
        units_text = response.css('.series-meta .meta-item:contains("Units:") + .meta-value::text').get()
        if units_text:
            info['units'] = units_text.strip()
        
        # Extract frequency
        freq_text = response.css('.series-meta .meta-item:contains("Frequency:") + .meta-value::text').get()
        if freq_text:
            info['frequency'] = freq_text.strip()
        
        # Extract seasonal adjustment
        sa_text = response.css('.series-meta .meta-item:contains("Seasonal Adjustment:") + .meta-value::text').get()
        if sa_text:
            info['seasonal_adjustment'] = sa_text.strip()
        
        # Extract last updated
        updated_text = response.css('.series-meta .meta-item:contains("Last Updated:") + .meta-value::text').get()
        if updated_text:
            info['last_updated'] = updated_text.strip()
        
        return info
    
    def extract_data_points(self, response) -> List[Dict]:
        """Extract data points from the page HTML"""
        data_points = []
        
        # Look for data in script tags (JSON data)
        script_data = response.css('script:contains("chartData")::text').getall()
        for script in script_data:
            if 'chartData' in script:
                # Extract JSON data from script
                json_match = re.search(r'chartData\s*=\s*(\[.*?\]);', script)
                if json_match:
                    try:
                        chart_data = json.loads(json_match.group(1))
                        for point in chart_data:
                            if isinstance(point, dict) and 'date' in point and 'value' in point:
                                parsed_date = datetime.strptime(point['date'], '%Y-%m-%d').date()
                                data_point = FredDataPoint(
                                    date=parsed_date.isoformat(),
                                    value=float(point['value']),
                                    period=f"{parsed_date.year}-{parsed_date.month:02d}",
                                    year=parsed_date.year,
                                    month=parsed_date.month
                                )
                                data_points.append(dict(data_point))
                    except (json.JSONDecodeError, ValueError, KeyError):
                        continue
        
        return data_points
    
    def get_download_url(self, response, series_id: str) -> Optional[str]:
        """Get CSV download URL for the series"""
        # Look for download link
        download_link = response.css('a[href*="downloaddata"]:contains("CSV")::attr(href)').get()
        if download_link:
            return urljoin(response.url, download_link)
        
        # Construct download URL manually
        base_url = "https://fred.stlouisfed.org/graph/fredgraph.csv"
        return f"{base_url}?id={series_id}" 