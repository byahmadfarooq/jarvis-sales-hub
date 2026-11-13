import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.gemini_engine import GeminiBrain
from backend.voice_engine import VoiceEngine
from backend.email_engine import EmailEngine
from backend.scraper_engine import LeadScraper
from backend.sheets_engine import CRMDatabase

app = FastAPI(title="Jarvis Executive Sales Hub", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate engines
db = CRMDatabase()
gemini = GeminiBrain()
voice = VoiceEngine()
email_engine = EmailEngine()
scraper = LeadScraper()

# Request Models
class ChatRequest(BaseModel):
    message: str
    with_voice: bool = True

class ScrapeRequest(BaseModel):
    niche: str
    location: str
    max_leads: int = 8

class DraftRequest(BaseModel):
    lead_id: int

class SendEmailRequest(BaseModel):
    lead_id: int
    subject: str
    body: str
    sender_alias: str = "Hostinger"

class CampaignUpdate(BaseModel):
    company_name: str
    offer: str
    booking_url: str
    target_niche: str
    whatsapp_number: str
    primary_sender: str

# ----------------- API ENDPOINTS -----------------

@app.get("/api/stats")
def get_dashboard_stats():
    stats = db.get_stats()
    campaign = db.get_campaign()
    return {"stats": stats, "campaign": campaign}

@app.get("/api/leads")
def get_leads(status: str = None):
    return db.get_leads(status=status)

@app.post("/api/chat")
async def chat_with_jarvis(req: ChatRequest):
    campaign = db.get_campaign()
    stats = db.get_stats()
    context = {"stats": stats, "campaign": campaign}
    
    # Generate structured answer (display markdown + fluid spoken summary)
    res_data = gemini.chat_assistant(req.message, context=context)
    display_md = res_data.get("display_markdown", "")
    spoken_text = res_data.get("spoken_summary", "")

    # Generate British neural voice on the fluid spoken summary
    audio_b64 = None
    if req.with_voice and spoken_text:
        try:
            audio_b64 = await voice.text_to_speech_base64(spoken_text)
        except Exception as e:
            print("Voice generation warning:", e)

    return {
        "reply": display_md,
        "spoken": spoken_text,
        "audio_base64": audio_b64
    }

@app.post("/api/voice_chat")
async def voice_chat_upload(file: UploadFile = File(...)):
    """Receives direct microphone audio from browser, processes via Gemini, speaks back."""
    campaign = db.get_campaign()
    stats = db.get_stats()
    context = {"stats": stats, "campaign": campaign}

    audio_bytes = await file.read()
    mime_type = file.content_type or "audio/webm"

    # Multimodal processing with Gemini
    ai_result = gemini.process_voice_audio(audio_bytes, mime_type=mime_type, context=context)
    user_transcript = ai_result.get("transcribed_user_text", "Voice message")
    display_md = ai_result.get("display_markdown", "")
    spoken_text = ai_result.get("spoken_summary", "")

    audio_b64 = None
    if spoken_text:
        try:
            audio_b64 = await voice.text_to_speech_base64(spoken_text)
        except Exception as e:
            print("Voice error:", e)

    return {
        "user_transcript": user_transcript,
        "reply": display_md,
        "spoken": spoken_text,
        "audio_base64": audio_b64
    }

@app.post("/api/scrape")
def scrape_leads(req: ScrapeRequest):
    results = scraper.scrape_and_enrich(req.niche, req.location, max_leads=req.max_leads)
    added_count = 0
    for r in results:
        if db.add_lead(r):
            added_count += 1
    return {
        "found": len(results),
        "added_to_crm": added_count,
        "leads": results
    }

@app.post("/api/draft")
def draft_email_for_lead(req: DraftRequest):
    leads = [l for l in db.get_leads() if l["id"] == req.lead_id]
    if not leads:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead = leads[0]
    campaign = db.get_campaign()
    draft = gemini.draft_cold_email(lead, campaign)
    return {"lead": lead, "draft": draft}

@app.post("/api/send")
def send_outreach_email(req: SendEmailRequest):
    leads = [l for l in db.get_leads() if l["id"] == req.lead_id]
    if not leads:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead = leads[0]

    result = email_engine.send_email(
        to_email=lead["email"],
        subject=req.subject,
        body=req.body,
        sender_alias=req.sender_alias
    )

    if result.get("success"):
        db.update_lead_status(
            lead_id=lead["id"],
            status="Contacted",
            subject=req.subject,
            body=req.body
        )
    return result

@app.get("/api/inbox/check")
def check_inbox_replies():
    replies = email_engine.check_inbound_replies(limit=10)
    analyzed = []
    for r in replies:
        analysis = gemini.analyze_reply(r.get("body", ""))
        analyzed.append({
            "from": r.get("from"),
            "subject": r.get("subject"),
            "date": r.get("date"),
            "body": r.get("body"),
            "analysis": analysis
        })
    return {"count": len(analyzed), "replies": analyzed}

@app.post("/api/campaign")
def update_campaign(data: CampaignUpdate):
    db.update_campaign(data.dict())
    return {"success": True, "campaign": db.get_campaign()}

# Mount Static Data directory (for audio files)
DATA_DIR = Path("D:/jarvis-sales-hub/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# Mount Static Frontend
FRONTEND_DIR = Path("D:/jarvis-sales-hub/frontend")
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
