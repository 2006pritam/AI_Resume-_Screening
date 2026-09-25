"""
Streamlit application root entrypoint.
Allows deploying using either 'app.py' or 'streamlit_app.py' on Streamlit Community Cloud.
"""
import os
import sys
from pathlib import Path
import runpy

# Ensure default backend URL points to the Render service
os.environ.setdefault("FASTAPI_URL", "https://ai-resume-screening-ik9s.onrender.com")
os.environ.setdefault("RENDER_URL", "https://ai-resume-screening-ik9s.onrender.com")

REPO_ROOT = Path(__file__).resolve().parent
STREAMLIT_APP_DIR = REPO_ROOT / "ai-resume-screener" / "streamlit"
APP_SCRIPT = STREAMLIT_APP_DIR / "app.py"

if not APP_SCRIPT.exists():
    raise FileNotFoundError(
        f"Streamlit application script not found at: {APP_SCRIPT}"
    )

sys.path.insert(0, str(STREAMLIT_APP_DIR))
runpy.run_path(str(APP_SCRIPT), run_name="__main__")
