import os
import smtplib
import imaplib
from pathlib import Path
import httpx
from google import genai

# Load env file manually
env_file = Path("D:/jarvis-sales-hub/.env")
env = {}
for line in env_file.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()

print("--- 1. Testing Telegram Bot ---")
bot_token = env.get("TELEGRAM_BOT_TOKEN")
chat_id = env.get("TELEGRAM_CHAT_ID")
try:
    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    r = httpx.post(tg_url, json={
        "chat_id": chat_id,
        "text": "⚡ Jarvis Core Online: Connected to ZotirLabs Sales & Outreach Engine."
    }, timeout=10.0)
    data = r.json()
    if data.get("ok"):
        print("Telegram: SUCCESS! Notification sent to your device.")
    else:
        print("Telegram Response:", data)
except Exception as e:
    print("Telegram Error:", e)

print("\n--- 2. Testing Google Gemini 2.5 Flash ---")
gemini_key = env.get("GEMINI_API_KEY")
try:
    client = genai.Client(api_key=gemini_key)
    # Check default gemini models
    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say exactly: Hello Ahmad, Jarvis intelligence is online and ready."
    )
    print("Gemini Response:", res.text.strip())
except Exception as e:
    print("Gemini Error:", e)

print("\n--- 3. Testing Hostinger SMTP (harvey@zotirlabs.com) ---")
hostinger_email = env.get("HOSTINGER_EMAIL")
hostinger_pwd = env.get("HOSTINGER_PASSWORD")
smtp_host = env.get("HOSTINGER_SMTP_HOST", "smtp.hostinger.com")
smtp_port = int(env.get("HOSTINGER_SMTP_PORT", 465))
try:
    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
        server.login(hostinger_email, hostinger_pwd)
        print("Hostinger SMTP: SUCCESS! Authenticated as", hostinger_email)
except Exception as e:
    print("Hostinger SMTP Error:", e)

print("\n--- 4. Testing Hostinger IMAP ---")
imap_host = env.get("HOSTINGER_IMAP_HOST", "imap.hostinger.com")
imap_port = int(env.get("HOSTINGER_IMAP_PORT", 993))
try:
    with imaplib.IMAP4_SSL(imap_host, imap_port) as mail:
        mail.login(hostinger_email, hostinger_pwd)
        mail.select("INBOX")
        typ, data = mail.search(None, "ALL")
        msg_count = len(data[0].split()) if data and data[0] else 0
        print(f"Hostinger IMAP: SUCCESS! Connected to INBOX ({msg_count} messages found).")
except Exception as e:
    print("Hostinger IMAP Error:", e)
