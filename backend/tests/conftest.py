import os
import sys

# Ensure backend/functions is on sys.path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "functions"))
if FUNCTIONS_DIR not in sys.path:
    sys.path.insert(0, FUNCTIONS_DIR)
