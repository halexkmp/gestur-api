# Vercel serverless entrypoint for FastAPI
# It imports the app instance from app.main and exposes it as `app`.
# Vercel will detect this and serve the ASGI application.

import sys
from pathlib import Path

# Ensure project root is on sys.path so `app` package can be imported when executed from /api
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the FastAPI app
from app.main import app  # noqa: E402  (import after path tweak)
