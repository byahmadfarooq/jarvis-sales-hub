import sys
import os
from pathlib import Path

# Set environment marker for Vercel serverless execution
os.environ["VERCEL"] = "1"

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.server import app
