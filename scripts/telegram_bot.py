import os
import sys
import time
import httpx
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from backend.gemini_engine import GeminiBrain
from backend.sheets_engine import CRMDatabase

def get_env():
    env_file = PROJECT_ROOT / ".env"
    env = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

env = get_env()
BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = env.get("TELEGRAM_CHAT_ID")
PROXY = env.get("TELEGRAM_PROXY")  # e.g. http://127.0.0.1:10808 or socks5://...

def send_telegram_alert(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram token or Chat ID missing.")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    client_args = {"timeout": 15.0}
    if PROXY:
        client_args["proxy"] = PROXY

    try:
        with httpx.Client(**client_args) as client:
            r = client.post(url, json=payload)
            return r.json().get("ok", False)
    except Exception as e:
        print(f"Telegram alert error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("⚡ TELEGRAM BOT ALERT WORKER FOR JARVIS")
    print(f"Target Chat ID: {CHAT_ID}")
    print("=" * 60)
    success = send_telegram_alert("⚡ *Jarvis Online*: ZotirLabs Sales & Outreach Bridge connected.")
    if success:
        print("SUCCESS! Test notification delivered to your Telegram.")
    else:
        print("Note: If api.telegram.org timed out, turn on Cloudflare 1.1.1.1 WARP or set TELEGRAM_PROXY in .env.")
