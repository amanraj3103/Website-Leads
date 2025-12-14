from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from integrations.google_sheets import GoogleSheetsManager
    GOOGLE_SHEETS_AVAILABLE = True
except Exception as e:
    GOOGLE_SHEETS_AVAILABLE = False
    logger.error(f"Failed to import GoogleSheetsManager: {e}")

sheets_manager = None
if GOOGLE_SHEETS_AVAILABLE:
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    if spreadsheet_id:
        try:
            sheets_manager = GoogleSheetsManager(credentials_file=None, spreadsheet_id=spreadsheet_id)
            if not (sheets_manager and sheets_manager.initialized):
                GOOGLE_SHEETS_AVAILABLE = False
        except Exception as e:
            sheets_manager = None
            GOOGLE_SHEETS_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_success(self):
        """Send success response with fallbacks"""
        response = b'{"success":true,"message":"Lead submitted successfully"}'
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response)
            return True
        except:
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response)
                return True
            except:
                try:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"success":true}')
                    return True
                except:
                    return False
    
    def do_POST(self):
        validation_passed = False
        try:
            # Parse
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            
            # Validate
            required = ['service', 'name', 'phone', 'email', 'place']
            if any(not data.get(f) for f in required):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
                return
            
            service = data.get('service')
            if service == 'Education India' and (not data.get('education_place') or not data.get('course')):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing fields for Education India'}).encode())
                return
            elif service == 'Education Abroad' and not data.get('education_country'):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing field for Education Abroad'}).encode())
                return
            elif service == 'Job Europe' and not data.get('work'):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing field for Job Europe'}).encode())
                return
            
            validation_passed = True
            
            # Save to Google Sheets (non-blocking)
            if GOOGLE_SHEETS_AVAILABLE and sheets_manager and sheets_manager.initialized:
                try:
                    sheets_data = {
                        'user_id': '', 'service_type': service, 'place': data.get('place'),
                        'name': data.get('name'), 'phone': data.get('phone'), 'email': data.get('email'),
                        'documents': '', 'notes': ''
                    }
                    if service == 'Education India':
                        sheets_data['notes'] = f"Place: {data.get('education_place')} | Course: {data.get('course')}"
                    elif service == 'Education Abroad':
                        sheets_data['notes'] = f"Country: {data.get('education_country')}"
                    elif service == 'Job Europe':
                        sheets_data['notes'] = f"Job Type: {data.get('work')}"
                    sheets_manager.save_lead(sheets_data)
                except Exception as e:
                    logger.error(f"Google Sheets error: {e}")
            
            # ALWAYS return success
            self._send_success()
            
        except Exception as e:
            logger.error(f"Exception: {e}", exc_info=True)
            if validation_passed:
                # Still return success if validation passed
                self._send_success()
            else:
                # Return error only if validation failed
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Internal server error'}).encode())
                except:
                    pass
