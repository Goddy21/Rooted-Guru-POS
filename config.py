"""
config.py — central place for all environment-driven settings.
Reads from .env in the same directory as the running exe/script.
Place this file at the project root alongside main.py.
"""

import os
import sys
from dotenv import load_dotenv


def _env_path():
    """
    Find .env next to the exe (PyInstaller) or next to main.py (dev).
    Works whether running as:
      - python main.py          (base = project root)
      - dist/RootedGuruPOS.exe  (base = folder containing the exe)
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller: exe lives in sys.executable's folder
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath('.')
    return os.path.join(base, '.env')


# Load .env — silent if file is missing (falls back to os.environ or defaults)
load_dotenv(_env_path())

# MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB  = os.getenv('MONGO_DB',  'silverpos')
