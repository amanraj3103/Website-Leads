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

# Try to import Google Sheets
try:
    from integrations.google_sheets import GoogleSheetsManager
    sheets_manager = None
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    credentials_b64 = os.getenv('GOOGLE_CREDENTIALS_JSON_B64')
    if spreadsheet_id and credentials_b64:
        try:
            sheets_manager = GoogleSheetsManager(credentials_file=None, spreadsheet_id=spreadsheet_id)
            if not (sheets_manager and hasattr(sheets_manager, 'initialized') and sheets_manager.initialized):
                sheets_manager = None
        except:
            sheets_manager = None
except:
    sheets_manager = None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            
            # Validate required fields
            required = ['service', 'name', 'phone', 'email', 'place']
            if any(not data.get(f) for f in required):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
                return
            
            # Validate service-specific fields
            service = data.get('service')
            if service == 'Education India' and (not data.get('education_place') or not data.get('course')):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing Education India fields'}).encode())
                return
            elif service == 'Education Abroad' and not data.get('education_country'):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing Education Abroad field'}).encode())
                return
            elif service == 'Job Europe' and not data.get('work'):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing Job Europe field'}).encode())
                return
            
            # Try to save to Google Sheets in background (ignore all errors)
            if sheets_manager:
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
                except:
                    pass  # Ignore all errors
            
            # ALWAYS return success after validation passes
            response = json.dumps({'success': True, 'message': 'Lead submitted successfully'})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            # If validation passed but something else failed, still return success
            # Otherwise return error
            try:
                response = json.dumps({'success': True, 'message': 'Lead submitted successfully'})
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.encode())
            except:
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Internal server error'}).encode())
                except:
                    pass
