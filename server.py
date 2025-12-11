#!/usr/bin/env python3
"""
Backend server for Dream Axis Lead Collection Website
Handles form submissions and saves to daily_leads.json
"""

import os
import json
import logging
import sys
from datetime import datetime, date
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Load environment variables from .env file in Website_assistant directory
BASE_DIR = Path(__file__).parent
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)
    logger.info(f"Loaded environment variables from {env_file}")
else:
    logger.info(f"No .env file found at {env_file}")

# Try to import Google Sheets integration from local integrations directory
# This is optional - the website works without it
try:
    from integrations.google_sheets import GoogleSheetsManager
    import os
    
    # Initialize Google Sheets manager with local credentials
    credentials_file = BASE_DIR / 'google_credentials.json'
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    
    sheets_manager = GoogleSheetsManager(
        credentials_file=str(credentials_file),
        spreadsheet_id=spreadsheet_id
    )
    
    GOOGLE_SHEETS_AVAILABLE = sheets_manager.initialized
    if GOOGLE_SHEETS_AVAILABLE:
        logger.info("Google Sheets integration loaded successfully")
    else:
        logger.warning("Google Sheets integration failed to initialize")
except ImportError as e:
    GOOGLE_SHEETS_AVAILABLE = False
    logger.warning(f"Google Sheets integration not available: {e}")
except Exception as e:
    GOOGLE_SHEETS_AVAILABLE = False
    sheets_manager = None
    logger.warning(f"Google Sheets integration error: {e}")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to daily_leads.json (in Website_assistant directory)
DAILY_LEADS_FILE = BASE_DIR / 'daily_leads.json'

def load_daily_leads():
    """Load daily leads from JSON file"""
    try:
        if DAILY_LEADS_FILE.exists():
            with open(DAILY_LEADS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading daily leads: {e}")
    return {}

def save_daily_leads(data):
    """Save daily leads to JSON file"""
    try:
        with open(DAILY_LEADS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving daily leads: {e}")
        return False

def save_lead_to_daily_data(lead_data):
    """Save lead data to daily storage"""
    today = date.today().strftime("%d_%m_%Y")
    
    # Load existing data
    daily_leads = load_daily_leads()
    
    if today not in daily_leads:
        daily_leads[today] = []
    
    # Add timestamp to lead data
    lead_data['timestamp'] = datetime.now().strftime("%H:%M:%S")
    daily_leads[today].append(lead_data)
    
    # Save to JSON file
    if save_daily_leads(daily_leads):
        logger.info(f"Lead saved successfully for {today}")
        return True
    else:
        logger.error("Failed to save lead data")
        return False

@app.route('/api/submit-lead', methods=['POST'])
def submit_lead():
    """Handle lead form submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service', 'name', 'phone', 'email', 'place']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate service-specific fields
        service = data.get('service')
        if service == 'Education India':
            if not data.get('education_place') or not data.get('course'):
                return jsonify({
                    'error': 'Missing required fields for Education India: education_place, course'
                }), 400
        elif service == 'Education Abroad':
            if not data.get('education_country'):
                return jsonify({
                    'error': 'Missing required field for Education Abroad: education_country'
                }), 400
        elif service == 'Job Europe':
            if not data.get('work'):
                return jsonify({
                    'error': 'Missing required field for Job Europe: work'
                }), 400
        
        # Prepare lead data
        lead_data = {
            'service': service,
            'name': data.get('name'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'place': data.get('place')
        }
        
        # Add service-specific data
        if service == 'Education India':
            lead_data['education_place'] = data.get('education_place')
            lead_data['course'] = data.get('course')
        elif service == 'Education Abroad':
            lead_data['education_country'] = data.get('education_country')
        elif service == 'Job Europe':
            lead_data['work'] = data.get('work')
        
        # Save lead data to daily_leads.json
        json_saved = save_lead_to_daily_data(lead_data)
        
        # Save to Google Sheets if available
        sheets_saved = False
        if GOOGLE_SHEETS_AVAILABLE and sheets_manager:
            try:
                # Prepare data for Google Sheets (matching expected format)
                sheets_data = {
                    'user_id': '',  # Not applicable for web form
                    'service_type': lead_data.get('service', ''),
                    'place': lead_data.get('place', ''),
                    'name': lead_data.get('name', ''),
                    'phone': lead_data.get('phone', ''),
                    'email': lead_data.get('email', ''),
                    'documents': '',
                    'notes': ''
                }
                
                # Add service-specific details to notes
                notes_parts = []
                if service == 'Education India':
                    notes_parts.append(f"Place: {lead_data.get('education_place', '')}")
                    notes_parts.append(f"Course: {lead_data.get('course', '')}")
                elif service == 'Education Abroad':
                    notes_parts.append(f"Country: {lead_data.get('education_country', '')}")
                elif service == 'Job Europe':
                    notes_parts.append(f"Job Type: {lead_data.get('work', '')}")
                
                if notes_parts:
                    sheets_data['notes'] = ' | '.join(notes_parts)
                
                sheets_saved = sheets_manager.save_lead(sheets_data)
                if sheets_saved:
                    logger.info("Lead saved to Google Sheets successfully")
                else:
                    logger.warning("Failed to save lead to Google Sheets, but continuing...")
            except Exception as e:
                logger.error(f"Error saving to Google Sheets: {e}")
        
        # Return success if at least one save method worked
        if json_saved:
            message = 'Lead submitted successfully'
            if sheets_saved:
                message += ' and saved to Google Sheets'
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'error': 'Failed to save lead data'
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing lead submission: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Dream Axis Lead Collection API'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Serve the index page"""
    return send_from_directory(Path(__file__).parent, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    static_dir = Path(__file__).parent
    
    # Security: Prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Access denied'}), 403
    
    file_path = static_dir / filename
    
    # First, try to serve from Website_assistant directory
    if file_path.exists() and file_path.is_file():
        # Additional security check
        try:
            file_path.resolve().relative_to(static_dir.resolve())
        except ValueError:
            return jsonify({'error': 'Access denied'}), 403
        return send_from_directory(static_dir, filename)
    
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Dream Axis Lead Collection Server on {host}:{port}")
    app.run(host=host, port=port, debug=True)

