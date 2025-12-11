#!/usr/bin/env python3
"""
Google Sheets Integration for Dream Axis Lead Collection Website
Automatically saves collected lead data to Google Sheets
"""

import os
import logging
import base64
import tempfile
from typing import Dict, List, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
from pathlib import Path

logger = logging.getLogger(__name__)

def _credentials_path_from_env_or_file(default_path: str) -> str:
    """
    Resolve a credentials file path. Supports base64-encoded credentials via
    GOOGLE_CREDENTIALS_JSON_B64. Falls back to a provided file path.
    """
    b64_creds = os.getenv("GOOGLE_CREDENTIALS_JSON_B64")
    if b64_creds:
        try:
            decoded = base64.b64decode(b64_creds).decode("utf-8")
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            tmp.write(decoded.encode("utf-8"))
            tmp.close()
            return tmp.name
        except Exception as e:
            logger.error(f"Error decoding GOOGLE_CREDENTIALS_JSON_B64: {e}")
            return default_path
    return default_path


class GoogleSheetsManager:
    def __init__(self, credentials_file: str = None, spreadsheet_id: str = None):
        self.sheets_client = None
        self.spreadsheet = None
        self.worksheet = None
        self.initialized = False
        
        # Google Sheets API scope
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Use provided paths or defaults, with env override for credentials
        if credentials_file is None:
            credentials_file = Path(__file__).parent.parent / 'google_credentials.json'
        resolved_creds = _credentials_path_from_env_or_file(str(credentials_file))

        if spreadsheet_id is None:
            spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
        
        self.credentials_file = resolved_creds
        self.spreadsheet_id = spreadsheet_id
        
        self._initialize_sheets()
    
    def _initialize_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_file):
                logger.warning(f"Google credentials file not found at {self.credentials_file}. Google Sheets integration disabled.")
                return
            
            if not self.spreadsheet_id:
                logger.warning("GOOGLE_SPREADSHEET_ID not found in environment. Google Sheets integration disabled.")
                return
            
            # Load credentials
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=self.scope)
            self.sheets_client = gspread.authorize(creds)
            
            # Open spreadsheet
            self.spreadsheet = self.sheets_client.open_by_key(self.spreadsheet_id)
            self.worksheet = self.spreadsheet.sheet1
            
            # Ensure headers exist
            self._ensure_headers()
            
            self.initialized = True
            logger.info(f"Google Sheets integration initialized successfully! Spreadsheet: {self.spreadsheet.title}")
            
        except GoogleAuthError as e:
            logger.error(f"Google authentication error: {e}")
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
    
    def _ensure_headers(self):
        """Ensure the worksheet has proper headers"""
        if not self.worksheet:
            return
            
        try:
            # Get existing headers
            headers = self.worksheet.row_values(1)
            
            # Define required headers
            required_headers = [
                'User ID',
                'Timestamp',
                'Service Type',
                'Place/Location',
                'Full Name',
                'Phone Number',
                'Email',
                'Status',
                'Documents',
                'Notes'
            ]
            
            # Check if headers need to be added
            if not headers or len(headers) < len(required_headers):
                self.worksheet.update('A1:J1', [required_headers])
                logger.info("Google Sheets headers updated")
                
        except Exception as e:
            logger.error(f"Error ensuring headers: {e}")
    
    def save_lead(self, lead_data: Dict) -> bool:
        """
        Save lead data to Google Sheets
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.initialized or not self.worksheet:
            logger.warning("Google Sheets not initialized. Cannot save lead.")
            return False
        
        try:
            # Prepare row data
            row_data = [
                lead_data.get('user_id', ''),                  # User ID
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Timestamp
                lead_data.get('service_type', ''),             # Service Type
                lead_data.get('place', ''),                    # Place/Location
                lead_data.get('name', ''),                     # Full Name
                lead_data.get('phone', ''),                    # Phone Number
                lead_data.get('email', ''),                    # Email
                'New Lead',                                    # Status
                lead_data.get('documents', ''),                # Documents
                lead_data.get('notes', '')                     # Notes
            ]
            
            # Append row to worksheet
            self.worksheet.append_row(row_data)
            
            logger.info(f"Lead saved to Google Sheets: {lead_data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving lead to Google Sheets: {e}")
            return False
    
    def get_all_leads(self) -> List[Dict]:
        """Get all leads from Google Sheets"""
        if not self.initialized or not self.worksheet:
            return []
        
        try:
            # Get all data
            all_data = self.worksheet.get_all_records()
            return all_data
            
        except Exception as e:
            logger.error(f"Error getting leads from Google Sheets: {e}")
            return []
    
    def update_lead_status(self, row_number: int, status: str) -> bool:
        """Update lead status in Google Sheets"""
        if not self.initialized or not self.worksheet:
            return False
        
        try:
            # Status is in column H (8th column)
            cell = f'H{row_number + 2}'  # +2 because row 1 is headers and sheets are 1-indexed
            self.worksheet.update(cell, status)
            return True
            
        except Exception as e:
            logger.error(f"Error updating lead status: {e}")
            return False

# Global instance will be created by server.py
sheets_manager = None

