import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from pathlib import Path
from datetime import datetime

def get_env():
    env_file = Path("D:/jarvis-sales-hub/.env")
    env = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

class EmailEngine:
    def __init__(self):
        self.env = get_env()
        self.hostinger_email = self.env.get("HOSTINGER_EMAIL", "harvey@zotirlabs.com")
        self.hostinger_pwd = self.env.get("HOSTINGER_PASSWORD", "")
        self.smtp_host = self.env.get("HOSTINGER_SMTP_HOST", "smtp.hostinger.com")
        self.smtp_port = int(self.env.get("HOSTINGER_SMTP_PORT", 465))
        self.imap_host = self.env.get("HOSTINGER_IMAP_HOST", "imap.hostinger.com")
        self.imap_port = int(self.env.get("HOSTINGER_IMAP_PORT", 993))
        
        # Secondary Gmail account
        self.gmail_user = self.env.get("GMAIL_USER")
        self.gmail_pwd = self.env.get("GMAIL_APP_PASSWORD")

    def send_email(self, to_email: str, subject: str, body: str, sender_alias: str = "Hostinger", reply_to: str = None) -> dict:
        """Sends an email using Hostinger SMTP or secondary Gmail."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["To"] = to_email

        if sender_alias == "Gmail" and self.gmail_user and self.gmail_pwd:
            sender_addr = self.gmail_user
            msg["From"] = f"Harvey <{self.gmail_user}>"
            smtp_server = "smtp.gmail.com"
            smtp_port = 465
            username = self.gmail_user
            password = self.gmail_pwd
        else:
            sender_addr = self.hostinger_email
            msg["From"] = f"Harvey | ZotirLabs <{self.hostinger_email}>"
            smtp_server = self.smtp_host
            smtp_port = self.smtp_port
            username = self.hostinger_email
            password = self.hostinger_pwd

        if reply_to:
            msg["Reply-To"] = reply_to
        else:
            msg["Reply-To"] = sender_addr

        # Clean plain text and standard HTML wrapper
        msg.attach(MIMEText(body, "plain"))
        html_body = body.replace("\n", "<br>")
        html_wrapper = f"""
        <html>
            <body style="font-family: Arial, sans-serif; font-size: 14px; color: #222; line-height: 1.5;">
                {html_body}
            </body>
        </html>
        """
        msg.attach(MIMEText(html_wrapper, "html"))

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15) as server:
                server.login(username, password)
                server.sendmail(sender_addr, [to_email], msg.as_string())
            return {
                "success": True,
                "sent_at": datetime.utcnow().isoformat(),
                "sender": sender_addr,
                "recipient": to_email
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sender": sender_addr,
                "recipient": to_email
            }

    def check_inbound_replies(self, limit: int = 20) -> list:
        """Connects via IMAP to scan recent unread messages or replies."""
        replies = []
        try:
            with imaplib.IMAP4_SSL(self.imap_host, self.imap_port, timeout=15) as mail:
                mail.login(self.hostinger_email, self.hostinger_pwd)
                mail.select("INBOX")
                status, messages = mail.search(None, "ALL")
                if status != "OK" or not messages[0]:
                    return replies

                mail_ids = messages[0].split()
                # Get the most recent ones
                recent_ids = mail_ids[-limit:]

                for mid in reversed(recent_ids):
                    typ, data = mail.fetch(mid, "(RFC822)")
                    if typ != "OK":
                        continue
                    
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Extract sender
                    from_header = msg.get("From", "")
                    subject_header = msg.get("Subject", "")

                    # Extract body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get("Content-Disposition"))
                            if ctype == "text/plain" and "attachment" not in cdispo:
                                try:
                                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                                except Exception:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except Exception:
                            pass

                    replies.append({
                        "id": mid.decode("utf-8"),
                        "from": from_header,
                        "subject": subject_header,
                        "date": msg.get("Date", ""),
                        "body": body.strip()[:1000]
                    })
        except Exception as e:
            print("IMAP Check Error:", e)

        return replies
