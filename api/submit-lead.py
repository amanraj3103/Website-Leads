from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from integrations.google_sheets import GoogleSheetsManager
    GOOGLE_SHEETS_AVAILABLE = True
except Exception as e:
    GOOGLE_SHEETS_AVAILABLE = False
    sheets_manager = None

# Initialize Google Sheets if available
if GOOGLE_SHEETS_AVAILABLE:
    credentials_file = BASE_DIR / 'google_credentials.json'
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    
    if credentials_file.exists() and spreadsheet_id:
        try:
            sheets_manager = GoogleSheetsManager(
                credentials_file=str(credentials_file),
                spreadsheet_id=spreadsheet_id
            )
        except Exception as e:
            sheets_manager = None
            GOOGLE_SHEETS_AVAILABLE = False
    else:
        sheets_manager = None
        GOOGLE_SHEETS_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['service', 'name', 'phone', 'email', 'place']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }).encode())
                return
            
            # Validate service-specific fields
            service = data.get('service')
            if service == 'Education India':
                if not data.get('education_place') or not data.get('course'):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Missing required fields for Education India: education_place, course'
                    }).encode())
                    return
            elif service == 'Education Abroad':
                if not data.get('education_country'):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Missing required field for Education Abroad: education_country'
                    }).encode())
                    return
            elif service == 'Job Europe':
                if not data.get('work'):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Missing required field for Job Europe: work'
                    }).encode())
                    return
            
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
            
            # Save to Google Sheets if available
            sheets_saved = False
            if GOOGLE_SHEETS_AVAILABLE and sheets_manager:
                try:
                    # Prepare data for Google Sheets
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
                except Exception as e:
                    sheets_saved = False
            
            # Return success
            if sheets_saved:
                message = 'Lead submitted successfully and saved to Google Sheets'
            else:
                message = 'Lead submitted successfully'
                if not GOOGLE_SHEETS_AVAILABLE:
                    message += ' (Google Sheets not configured)'
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': message
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            }).encode())

