#!/usr/bin/env python3
"""
BLS Scraper API Server
Production-ready Flask API for BLS economic data scraping
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import BadRequest, InternalServerError
from dotenv import load_dotenv

# Import our scraper
from bls_scraper import load_data, get_available_indicators, clear_cache

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bls_api.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_VERSION = "1.0.0"
MAX_RESULTS = 1000

class APIError(Exception):
    """Custom API error class"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle custom API errors"""
    logger.error(f"API Error: {error.message}")
    return jsonify({
        'error': error.message,
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), error.status_code

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    """Handle bad request errors"""
    logger.error(f"Bad Request: {error.description}")
    return jsonify({
        'error': 'Bad request',
        'message': error.description,
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), 400

@app.errorhandler(InternalServerError)
def handle_internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal Server Error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), 500

@app.before_request
def log_request_info():
    """Log incoming requests"""
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def after_request(response):
    """Add CORS headers and log response"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
    return response

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        'name': 'BLS Scraper API',
        'version': API_VERSION,
        'description': 'Fast, reliable BLS economic data scraping API',
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /indicators': 'Available economic indicators',
            'GET /data/<ticker>': 'Get economic data for indicator',
            'POST /clear-cache': 'Clear data cache'
        },
        'example_usage': {
            'cpi_data': '/data/cpi?date=2022-2024',
            'unemployment': '/data/unemployment?date=last_3_years',
            'core_cpi': '/data/cpi_core?date=2023'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Quick test of core functionality
        test_data = load_data('cpi', '2024')
        is_healthy = len(test_data) > 0
        
        return jsonify({
            'status': 'healthy' if is_healthy else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'version': API_VERSION,
            'data_available': is_healthy,
            'cache_directory': os.path.exists('data_cache')
        }), 200 if is_healthy else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

@app.route('/indicators')
def get_indicators():
    """Get available economic indicators"""
    try:
        indicators = get_available_indicators()
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'indicators': indicators,
            'count': len(indicators)
        })
    except Exception as e:
        logger.error(f"Failed to get indicators: {e}")
        raise APIError("Failed to retrieve indicators", 500)

@app.route('/data/<ticker>')
def get_economic_data(ticker: str):
    """Get economic data for specified indicator"""
    try:
        # Validate ticker
        if not ticker or len(ticker.strip()) == 0:
            raise APIError("Ticker parameter is required")
        
        ticker = ticker.strip().lower()
        
        # Get date parameter
        date_param = request.args.get('date', None)
        
        # Get format parameter
        output_format = request.args.get('format', 'json').lower()
        if output_format not in ['json', 'csv']:
            raise APIError("Format must be 'json' or 'csv'")
        
        # Validate date format if provided
        if date_param:
            date_param = date_param.strip()
            if not date_param:
                date_param = None
        
        # Load data
        logger.info(f"Loading data for ticker: {ticker}, date: {date_param}")
        data = load_data(ticker, date_param)
        
        if not data:
            raise APIError(f"No data available for ticker '{ticker}' with date '{date_param}'", 404)
        
        # Limit results
        if len(data) > MAX_RESULTS:
            data = data[:MAX_RESULTS]
            logger.warning(f"Results limited to {MAX_RESULTS} entries")
        
        # Prepare response
        response_data = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'ticker': ticker,
            'date_range': date_param or 'default',
            'count': len(data),
            'data': data
        }
        
        if output_format == 'csv':
            # Convert to CSV format
            import io
            import csv
            
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={ticker}_data.csv'
            return response
        
        return jsonify(response_data)
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Failed to get data for {ticker}: {e}")
        raise APIError(f"Failed to retrieve data: {str(e)}", 500)

@app.route('/clear-cache', methods=['POST'])
def clear_data_cache():
    """Clear the data cache"""
    try:
        clear_cache()
        logger.info("Cache cleared successfully")
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise APIError("Failed to clear cache", 500)

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def create_app():
    """Application factory"""
    return app

def main():
    """Main entry point for production deployment"""
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting BLS Scraper API v{API_VERSION}")
    logger.info(f"Server: {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()