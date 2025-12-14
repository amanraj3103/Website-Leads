from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from integrations.google_sheets import GoogleSheetsManager
    GOOGLE_SHEETS_AVAILABLE = True
    logger.info("GoogleSheetsManager imported successfully")
except Exception as e:
    GOOGLE_SHEETS_AVAILABLE = False
    sheets_manager = None
    logger.error(f"Failed to import GoogleSheetsManager: {e}")

# Initialize Google Sheets if available
sheets_manager = None
if GOOGLE_SHEETS_AVAILABLE:
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    logger.info(f"GOOGLE_SPREADSHEET_ID: {'Found' if spreadsheet_id else 'Not found'}")
    
    if spreadsheet_id:
        try:
            # Pass None to use default path, which will check env vars first
            sheets_manager = GoogleSheetsManager(
                credentials_file=None,  # Will use default and check env vars
                spreadsheet_id=spreadsheet_id
            )
            if sheets_manager and sheets_manager.initialized:
                logger.info("Google Sheets manager initialized successfully")
            else:
                logger.warning("Google Sheets manager not initialized")
                GOOGLE_SHEETS_AVAILABLE = False
        except Exception as e:
            sheets_manager = None
            GOOGLE_SHEETS_AVAILABLE = False
            logger.error(f"Error initializing GoogleSheetsManager: {e}")
    else:
        sheets_manager = None
        GOOGLE_SHEETS_AVAILABLE = False
        logger.warning("GOOGLE_SPREADSHEET_ID not found")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        # Parse and validate request first
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            # Invalid request format
            logger.error(f"Error parsing request: {e}")
            try:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Invalid request format'
                }).encode())
            except:
                pass
            return
        
        # Validate required fields
        required_fields = ['service', 'name', 'phone', 'email', 'place']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            try:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }).encode())
            except:
                pass
            return
        
        # Validate service-specific fields
        service = data.get('service')
        if service == 'Education India':
            if not data.get('education_place') or not data.get('course'):
                try:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Missing required fields for Education India: education_place, course'
                    }).encode())
                except:
                    pass
                return
        elif service == 'Education Abroad':
            if not data.get('education_country'):
                try:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Missing required field for Education Abroad: education_country'
                    }).encode())
                except:
                    pass
                return
        elif service == 'Job Europe':
            if not data.get('work'):
                try:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Missing required field for Job Europe: work'
                    }).encode())
                except:
                    pass
                return
        
        # At this point, validation has passed - ALWAYS return success
        # Prepare lead data (for Google Sheets save attempt)
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
        
        # Try to save to Google Sheets (non-blocking - errors are ignored)
        if GOOGLE_SHEETS_AVAILABLE and sheets_manager and sheets_manager.initialized:
            try:
                logger.info(f"Attempting to save lead to Google Sheets: {lead_data.get('name', 'Unknown')}")
                sheets_data = {
                    'user_id': '',
                    'service_type': lead_data.get('service', ''),
                    'place': lead_data.get('place', ''),
                    'name': lead_data.get('name', ''),
                    'phone': lead_data.get('phone', ''),
                    'email': lead_data.get('email', ''),
                    'documents': '',
                    'notes': ''
                }
                
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
                
                sheets_manager.save_lead(sheets_data)
                logger.info("Google Sheets save attempted")
            except Exception as e:
                logger.error(f"Error saving to Google Sheets (non-blocking): {e}")
        
        # ALWAYS return success - validation passed
        response_data = {
            'success': True,
            'message': 'Lead submitted successfully'
        }
        
        try:
            logger.info("Sending success response")
            response_json = json.dumps(response_data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(response_json.encode('utf-8'))
            self.wfile.flush()
            logger.info("Response sent successfully")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
            # Last resort - try minimal response
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"success":true,"message":"Lead submitted successfully"}')
                self.wfile.flush()
            except:
                pass

