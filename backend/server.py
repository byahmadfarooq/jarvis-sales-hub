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

app = FastAPI(title="ZotirLabs Executive Sales Hub", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate core engines
db = CRMDatabase()
gemini = GeminiBrain()
voice = VoiceEngine()
email_engine = EmailEngine()
scraper = LeadScraper()

# Request Models
class ChatRequest(BaseModel):
    message: str
    with_voice: bool = True

class TTSRequest(BaseModel):
    text: str

class ScrapeRequest(BaseModel):
    niche: str
    location: str
    max_leads: int = 8

class DraftRequest(BaseModel):
    lead_id: int

class SendEmailRequest(BaseModel):
    lead_id: int = None
    recipient: str = None
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
    return {
        "stats": db.get_stats(),
        "campaign": db.get_campaign()
    }

@app.get("/api/leads")
def get_leads(status: str = None):
    return db.get_leads(status=status, limit=100)

@app.post("/api/chat")
async def chat_with_jarvis(req: ChatRequest):
    campaign = db.get_campaign()
    stats = db.get_stats()
    context = {"stats": stats, "campaign": campaign}

    # High-speed strategic generation
    res_data = gemini.chat_assistant(req.message, context=context)
    display_md = res_data.get("display_markdown", "")
    spoken_text = res_data.get("spoken_summary", "")
    suggestions = res_data.get("suggestions", [])

    audio_b64 = None
    if req.with_voice and spoken_text:
        try:
            # Generate British voice concurrently
            audio_b64 = await voice.text_to_speech_base64(spoken_text)
        except Exception as e:
            print("Voice generation error:", e)

    return {
        "reply": display_md,
        "spoken": spoken_text,
        "suggestions": suggestions,
        "audio_base64": audio_b64
    }

@app.post("/api/tts")
async def generate_tts(req: TTSRequest):
    try:
        b64 = await voice.text_to_speech_base64(req.text)
        return {"audio_base64": b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice_chat")
async def voice_chat_upload(file: UploadFile = File(...)):
    campaign = db.get_campaign()
    stats = db.get_stats()
    context = {"stats": stats, "campaign": campaign}

    audio_bytes = await file.read()
    mime_type = file.content_type or "audio/webm"

    ai_result = gemini.process_voice_audio(audio_bytes, mime_type=mime_type, context=context)
    user_transcript = ai_result.get("transcribed_user_text", "Voice query")
    display_md = ai_result.get("display_markdown", "")
    spoken_text = ai_result.get("spoken_summary", "")
    suggestions = ai_result.get("suggestions", [])

    audio_b64 = None
    if spoken_text:
        try:
            audio_b64 = await voice.text_to_speech_base64(spoken_text)
        except Exception as e:
            print("Voice generation error:", e)

    return {
        "user_transcript": user_transcript,
        "reply": display_md,
        "spoken": spoken_text,
        "suggestions": suggestions,
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
    target_email = req.recipient
    if not target_email and req.lead_id:
        leads = [l for l in db.get_leads() if l["id"] == req.lead_id]
        if leads:
            target_email = leads[0]["email"]

    if not target_email:
        raise HTTPException(status_code=400, detail="Recipient email not specified")

    import re
    extracted = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", target_email)
    if extracted:
        target_email = extracted[0]

    result = email_engine.send_email(
        to_email=target_email,
        subject=req.subject,
        body=req.body,
        sender_alias=req.sender_alias
    )

    if result.get("success") and req.lead_id:
        db.update_lead_status(
            lead_id=req.lead_id,
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

# Static File Mounting
FRONTEND_DIR = Path("D:/jarvis-sales-hub/frontend")
DATA_DIR = Path("D:/jarvis-sales-hub/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
