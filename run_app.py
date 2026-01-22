#!/usr/bin/env python3
"""
run_app.py

Launches the Streamlit application and exposes it via a Cloudflare
quick tunnel (trycloudflare.com). Intended for demos and sharing.
"""

!pip install streamlit

import subprocess

# Download and install cloudflared
subprocess.run(['wget', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'], check=True)
subprocess.run(['chmod', '+x', 'cloudflared-linux-amd64'], check=True)
subprocess.run(['sudo', 'mv', 'cloudflared-linux-amd64', '/usr/local/bin/cloudflared'], check=True)

print("cloudflared installed successfully.")

!killall -9 cloudflared
!killall -9 streamlitrun



import os
import sys
import time
import shutil
import subprocess
import re
import signal
from pathlib import Path

STREAMLIT_CMD = [
    sys.executable, "-m", "streamlit", "run",
    "app.py", "--server.port", "8501", "--server.address", "127.0.0.1"
]

STREAMLIT_LOG = Path("streamlit.log")
CLOUDFLARED_LOG = Path("cloudflared.log")
CLOUDFLARED_PATH = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"

TRYCLOUD_RE = re.compile(r"https?://[^\s]+trycloudflare\.com")


def ensure_cloudflared(path=CLOUDFLARED_PATH):
    path = Path(path)
    if path.exists() and os.access(path, os.X_OK):
        return str(path)
    raise RuntimeError("cloudflared not found. Please install it first.")


def start_streamlit():
    subprocess.run(["pkill", "-f", "streamlit"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = open(STREAMLIT_LOG, "ab")
    return subprocess.Popen(
        STREAMLIT_CMD,
        stdout=log,
        stderr=subprocess.STDOUT,
        env=os.environ.copy()
    )


def wait_for_port(host="127.0.0.1", port=8501, timeout=30):
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def start_cloudflared(bin_path):
    subprocess.run(["pkill", "-f", "cloudflared"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    args = [bin_path, "tunnel", "--url", "http://127.0.0.1:8501", "--no-autoupdate"]
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    with open(CLOUDFLARED_LOG, "w", encoding="utf-8") as log:
        for _ in range(60):
            line = proc.stdout.readline()
            if not line:
                break
            log.write(line)
            match = TRYCLOUD_RE.search(line)
            if match:
                public_url = match.group(0)
                break

    return public_url, proc


def main():
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

    cloudflared = ensure_cloudflared()
    st_proc = start_streamlit()

    if not wait_for_port():
        raise RuntimeError("Streamlit did not start correctly.")

    public_url, _ = start_cloudflared(cloudflared)

    if public_url:
        print("\n=== Public URL ===")
        print(public_url)
    else:
        print("Cloudflare tunnel started but no URL detected.")


if __name__ == "__main__":
    main()

