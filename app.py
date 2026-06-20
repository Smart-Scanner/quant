#!/usr/bin/env python3
"""
Smart Screener — Entry Point
NSE Stock Screener + Portfolio Manager with Angel One Live Feed
"""

import os
import time
import signal
import logging
import threading
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*no explicit representation of timezones.*",
    category=UserWarning,
)

from dotenv import load_dotenv
load_dotenv()

import sys
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("screener").info("System: Windows process priority set to BELOW_NORMAL.")
    except Exception:
        pass

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_compress import Compress

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("screener")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

from config import FLASK_SECRET_KEY
app.secret_key = FLASK_SECRET_KEY or "nse-screener-dev-key-change-me"
if not FLASK_SECRET_KEY:
    log.warning("FLASK_SECRET_KEY not set — using insecure dev key. Set it in .env before deploy.")

Compress(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.context_processor
def inject_template_globals():
    from datetime import datetime
    return {"current_year": datetime.now().year}

log.info("Smart Screener v6 | Stock Screener + Portfolio Manager")
log.info("Engine initialized successfully")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    app.run(debug=False, host="0.0.0.0", port=port)
