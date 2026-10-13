"""ScopeKernel Desktop Launcher & Debug Runner.

Launches the ScopeKernel local desktop application and opens the dashboard
in the user's default browser.
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    banner = r"""
  ____                         _  __                    _ 
 / ___|  ___ ___  _ __   ___  | |/ /___ _ __ _ __   ___| |
 \___ \ / __/ _ \| '_ \ / _ \ | ' // _ \ '__| '_ \ / _ \ |
  ___) | (_| (_) | |_) |  __/ | . \  __/ |  | | | |  __/ |
 |____/ \___\___/| .__/ \___| |_|\_\___|_|  |_| |_|\___|_|
                 |_|                                       
    The Air-Gapped Scope-Creep & Change-Order Engine
           Zero Cloud Telemetry • Gemma-2-2B
    """
    print(banner)

def check_environment():
    print("[*] Validating local runtime environment...")
    try:
        import pydantic
        import httpx
        import streamlit
        import pytest
        print(f"    [+] Pydantic {pydantic.__version__} (OK)")
        print(f"    [+] HTTPX {httpx.__version__} (OK)")
        print(f"    [+] Streamlit {streamlit.__version__} (OK)")
        print(f"    [+] Pytest {pytest.__version__} (OK)")
    except ImportError as e:
        print(f"    [!] Missing dependency: {e}")
        print("    [*] Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_ollama():
    try:
        import httpx
        resp = httpx.get("http://localhost:11434/api/tags", timeout=1.5)
        if resp.status_code == 200:
            print("    [+] Local Ollama daemon active on http://localhost:11434")
            models = [m.get("name") for m in resp.json().get("models", [])]
            print(f"    [+] Detected models: {', '.join(models) if models else 'None'}")
            return True
    except Exception:
        pass
    print("    [i] Note: Ollama not detected on localhost:11434.")
    print("        ScopeKernel will operate in Built-in Offline Deterministic Engine mode.")
    return False

def open_browser(url: str, delay: float = 1.5):
    import threading
    def _open():
        time.sleep(delay)
        print(f"[*] Opening browser at {url} ...")
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()

def main():
    print_banner()
    check_environment()
    check_ollama()

    app_path = Path(__file__).parent / "scopekernel" / "ui" / "app.py"
    if not app_path.exists():
        app_path = Path(__file__).parent / "ui" / "app.py"

    url = "http://localhost:8501"
    print(f"\n[*] Launching ScopeKernel dashboard at {url} ...")
    open_browser(url, delay=1.2)

    # Launch Streamlit server
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        "8501",
        "--server.headless",
        "false",
        "--browser.gatherUsageStats",
        "false",
    ]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[*] ScopeKernel shut down cleanly.")

if __name__ == "__main__":
    main()
