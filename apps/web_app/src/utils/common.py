import os
import time
import logging
from typing import Dict, List
import requests
from src.utils.pymodels import Vulnerability

# ---------- Global Variables ----------

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

BACKEND_HOST: str = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "5000"))
PORT: int = int(os.getenv("PORT", "8501"))
API_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# ---------- All util Functions ----------


def wait_for_backend(max_retries: int = 10, delay: int = 5) -> None:
    """Wait until management_api is healthy (up and responding)."""
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(f"{API_URL}/health", timeout=5)
            if r.status_code == 200:
                logger.info("✅ Backend is healthy.")
                return
        except requests.RequestException:
            pass
        logger.warning(f"⏳ Waiting for backend... (attempt {attempt}/{max_retries})")
        time.sleep(delay)
    raise RuntimeError("❌ Backend did not become healthy in time.")


def get_vulnerabilities() -> Dict[str, List[Vulnerability]]:
    """Fetch vulnerabilities from backend (title + code only, no category)."""

    wait_for_backend()

    r = requests.get(f"{API_URL}/vulnerabilities", timeout=60)
    data = r.json()

    vulns: Dict[str, List[Vulnerability]] = {}
    for codebase, vuln_list in data.items():
        vulns[codebase] = [Vulnerability(**v) for v in vuln_list]

    return vulns
