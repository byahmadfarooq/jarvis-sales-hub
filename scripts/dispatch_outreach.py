import sys
import time
from pathlib import Path

PROJECT_ROOT = Path("D:/jarvis-sales-hub")
sys.path.insert(0, str(PROJECT_ROOT))

from backend.sheets_engine import CRMDatabase
from backend.gemini_engine import GeminiBrain
from backend.email_engine import EmailEngine

def dispatch_all_new_leads():
    db = CRMDatabase()
    gemini = GeminiBrain()
    email_engine = EmailEngine()

    leads = db.get_leads(status="New")
    campaign = db.get_campaign()

    print(f"==================================================")
    print(f"DISPATCHING OUTREACH TO {len(leads)} NEW LEADS")
    print(f"Sender: {campaign.get('primary_sender', 'harvey@zotirlabs.com')}")
    print(f"CTA Booking URL: {campaign.get('booking_url', 'https://zotirlabs.com/book')}")
    print(f"==================================================\n")

    if not leads:
        print("No 'New' leads found in CRM to send to.")
        return

    sent_count = 0
    for l in leads:
        lead_id = l["id"]
        to_email = l["email"]
        company = l.get("company", "their practice")
        print(f"-> Generating bespoke teardown pitch for: {to_email} ({company})...")

        # 1. Generate tailored pitch via Gemini
        draft = gemini.draft_cold_email(l, campaign)
        subject = draft.get("subject", f"Quick website review for {company}")
        body = draft.get("body", "")

        # 2. Dispatch via Hostinger SMTP
        print(f"   Subject: {subject}")
        print(f"   Sending via Hostinger SMTP...")
        res = email_engine.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            sender_alias="Hostinger"
        )

        if res.get("success"):
            sent_count += 1
            db.update_lead_status(
                lead_id=lead_id,
                status="Contacted",
                subject=subject,
                body=body
            )
            print(f"   [SUCCESS] Dispatched to {to_email} & stored in Hostinger Sent folder.\n")
        else:
            print(f"   [FAILED] Error: {res.get('error')}\n")

        # Brief pacing delay to protect domain reputation
        time.sleep(3)

    print("==================================================")
    print(f"COMPLETED: {sent_count}/{len(leads)} emails successfully dispatched!")
    print("==================================================")

if __name__ == "__main__":
    dispatch_all_new_leads()
