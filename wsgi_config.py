# PythonAnywhere WSGI configuration
# Paste this into your PythonAnywhere WSGI file at:
# /var/www/xenohuru_pythonanywhere_com_wsgi.py
#
# In the PA Web tab, click "WSGI configuration file" link and replace ALL content with this.

import sys
import os
from pathlib import Path

# Project root on PythonAnywhere
PROJECT_ROOT = '/home/xenohuru/xenohuru-api'
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

# Add src/ to sys.path so Django can find 'cofig' and 'app.*'
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Load environment variables from .env
env_file = os.path.join(SRC_DIR, '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())

os.environ['DJANGO_SETTINGS_MODULE'] = 'cofig.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
