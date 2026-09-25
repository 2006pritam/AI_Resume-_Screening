"""
Streamlit deployment entrypoint for AI Resume Screening & Candidate Clustering.
This script delegates execution to the Streamlit app in ai-resume-screener/streamlit/app.py.
"""
import os
import sys
from pathlib import Path
import runpy

# Ensure default backend URL points to the Render service
os.environ.setdefault("FASTAPI_URL", "https://ai-resume-screening-ik9s.onrender.com")
os.environ.setdefault("RENDER_URL", "https://ai-resume-screening-ik9s.onrender.com")

# Resolve paths relative to this repository root
REPO_ROOT = Path(__file__).resolve().parent
STREAMLIT_APP_DIR = REPO_ROOT / "ai-resume-screener" / "streamlit"
APP_SCRIPT = STREAMLIT_APP_DIR / "app.py"

if not APP_SCRIPT.exists():
    raise FileNotFoundError(
        f"Streamlit application script not found at: {APP_SCRIPT}"
    )

# Add application directory to sys.path
sys.path.insert(0, str(STREAMLIT_APP_DIR))

# Execute the main Streamlit application
runpy.run_path(str(APP_SCRIPT), run_name="__main__")
