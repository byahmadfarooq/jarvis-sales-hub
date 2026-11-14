import os
import shutil
import sqlite3
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/crm_leads.db")
    if not DB_PATH.exists():
        seed = BASE_DIR / "data" / "crm_leads.db"
        if seed.exists():
            shutil.copyfile(seed, DB_PATH)
        else:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
else:
    DB_PATH = BASE_DIR / "data" / "crm_leads.db"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class CRMDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                company TEXT,
                website TEXT,
                phone TEXT,
                status TEXT DEFAULT 'New',
                source TEXT DEFAULT 'Scraper',
                last_contacted_at TEXT,
                last_subject TEXT,
                last_body TEXT,
                notes TEXT,
                created_at TEXT
            )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS campaign_settings (
                id INTEGER PRIMARY KEY,
                company_name TEXT DEFAULT 'ZotirLabs',
                offer TEXT DEFAULT 'Free 5-Minute Website Review',
                booking_url TEXT DEFAULT 'https://zotirlabs.com/book',
                target_niche TEXT DEFAULT 'B2B Services & Agencies',
                whatsapp_number TEXT DEFAULT '923427689885',
                primary_sender TEXT DEFAULT 'harvey@zotirlabs.com'
            )
            """)
            # Initialize default campaign row if empty
            cursor = conn.execute("SELECT COUNT(*) FROM campaign_settings")
            if cursor.fetchone()[0] == 0:
                conn.execute("""
                INSERT INTO campaign_settings (id, company_name, offer, booking_url, target_niche, whatsapp_number, primary_sender)
                VALUES (1, 'ZotirLabs', 'Free 5-Minute Website Review to Bring Enquiries', 'https://zotirlabs.com/book', 'B2B Services & Agencies', '923427689885', 'harvey@zotirlabs.com')
                """)

    def add_lead(self, lead: dict) -> bool:
        if not lead.get("email"):
            return False
        with self._get_conn() as conn:
            try:
                conn.execute("""
                INSERT INTO leads (name, email, company, website, phone, status, source, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    name=excluded.name,
                    company=excluded.company,
                    website=excluded.website
                """, (
                    lead.get("name", "Business Owner"),
                    lead.get("email").strip().lower(),
                    lead.get("company", ""),
                    lead.get("website", ""),
                    lead.get("phone", ""),
                    lead.get("status", "New"),
                    lead.get("source", "Scraper"),
                    lead.get("notes", ""),
                    datetime.utcnow().isoformat()
                ))
                return True
            except Exception as e:
                print(f"Error saving lead: {e}")
                return False

    def get_leads(self, status: str = None, limit: int = 100) -> list:
        with self._get_conn() as conn:
            if status:
                cursor = conn.execute("SELECT * FROM leads WHERE status = ? ORDER BY id DESC LIMIT ?", (status, limit))
            else:
                cursor = conn.execute("SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def update_lead_status(self, lead_id: int, status: str, subject: str = None, body: str = None):
        with self._get_conn() as conn:
            conn.execute("""
            UPDATE leads
            SET status = ?,
                last_contacted_at = ?,
                last_subject = COALESCE(?, last_subject),
                last_body = COALESCE(?, last_body)
            WHERE id = ?
            """, (status, datetime.utcnow().isoformat(), subject, body, lead_id))

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            new_leads = conn.execute("SELECT COUNT(*) FROM leads WHERE status = 'New'").fetchone()[0]
            contacted = conn.execute("SELECT COUNT(*) FROM leads WHERE status = 'Contacted'").fetchone()[0]
            replied = conn.execute("SELECT COUNT(*) FROM leads WHERE status IN ('Replied', 'Interested')").fetchone()[0]
            booked = conn.execute("SELECT COUNT(*) FROM leads WHERE status = 'Booked'").fetchone()[0]
            return {
                "total_leads": total,
                "new_leads": new_leads,
                "contacted": contacted,
                "replied": replied,
                "booked": booked
            }

    def get_campaign(self) -> dict:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM campaign_settings WHERE id = 1").fetchone()
            return dict(row) if row else {}

    def update_campaign(self, data: dict):
        with self._get_conn() as conn:
            conn.execute("""
            UPDATE campaign_settings
            SET company_name = ?,
                offer = ?,
                booking_url = ?,
                target_niche = ?,
                whatsapp_number = ?,
                primary_sender = ?
            WHERE id = 1
            """, (
                data.get("company_name", "ZotirLabs"),
                data.get("offer", ""),
                data.get("booking_url", ""),
                data.get("target_niche", ""),
                data.get("whatsapp_number", ""),
                data.get("primary_sender", "")
            ))

    def export_csv(self, output_path: str = None) -> str:
        if not output_path:
            output_path = str(self.db_path.parent / "leads_export.csv")
        leads = self.get_leads(limit=1000)
        if not leads:
            return ""
        keys = leads[0].keys()
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(leads)
        return output_path
