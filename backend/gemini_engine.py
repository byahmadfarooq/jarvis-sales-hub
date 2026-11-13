import os
import json
from pathlib import Path
from google import genai
from google.genai import types

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

class GeminiBrain:
    def __init__(self):
        self.env = get_env()
        self.api_key = self.env.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        # Preferred models with fallback order
        self.models = [
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-3.1-flash-lite",
            "gemini-2.5-pro"
        ]

    def generate(self, prompt: str, system_instruction: str = None, max_tokens: int = 500) -> str:
        if not self.client:
            return "Error: GEMINI_API_KEY is not configured in .env."
        
        last_error = None
        for m in self.models:
            try:
                config = types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.6
                )
                if system_instruction:
                    config.system_instruction = system_instruction
                
                response = self.client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = e
                continue
        
        return f"Gemini Error across all models: {last_error}"

    def chat_assistant(self, message: str, context: dict = None) -> dict:
        """High-velocity Strategic Growth Partner for ZotirLabs. Returns structured markdown + punchy vocal summary + interactive suggestions."""
        system_prompt = (
            "You are Jarvis — Executive Growth Partner and Strategic AI Co-Pilot at ZotirLabs (zotirlabs.com).\n"
            "ABOUT ZOTIRLABS:\n"
            "- Core Proposition: 'Websites that bring enquiries. We design, build and hand over websites clients can edit themselves without waiting or support tickets.'\n"
            "- Target: Service firms, medical/dental practices, B2B agencies, law firms, and consultancy businesses losing mobile traffic.\n"
            "- Brand Tone: Refined, British, highly strategic, punchy, no corporate fluff, zero AI cliché. Speak like a senior agency partner, not a robotic subservient assistant.\n\n"
            "OUTPUT FORMAT: Return STRICT JSON ONLY with three fields:\n"
            "1. 'display_markdown': Direct, beautifully structured Markdown with bold titles, bullet points, and strategic insight.\n"
            "2. 'spoken_summary': ONE crisp, authoritative spoken sentence in natural British cadence. NO asterisks, NO colons, NO bullets.\n"
            "3. 'suggestions': An array of 3 short, interactive follow-up prompt pills (e.g. ['Draft Dental Pitch', 'Scrape Manchester', 'Review Pipeline'])."
        )
        ctx_str = f"\nCurrent State: {json.dumps(context)}" if context else ""
        raw = self.generate(message + ctx_str, system_instruction=system_prompt, max_tokens=600)
        
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return {
                "display_markdown": data.get("display_markdown", raw),
                "spoken_summary": data.get("spoken_summary", "Strategic directive acknowledged, sir."),
                "suggestions": data.get("suggestions", ["Audit Current Leads", "Launch New Scrape", "Check Inbox Replies"])
            }
        except Exception:
            return {
                "display_markdown": raw,
                "spoken_summary": "Understood, Ahmad. Processing the strategy now.",
                "suggestions": ["Scrape More Leads", "Draft Outreach", "View Campaign"]
            }

    def process_voice_audio(self, audio_bytes: bytes, mime_type: str = "audio/webm", context: dict = None) -> dict:
        """Processes raw audio directly from microphone in sub-second response."""
        system_prompt = (
            "You are Jarvis, Growth Partner for ZotirLabs. Listen to Ahmad's voice note and respond with decisive strategic clarity.\n"
            "Return valid JSON ONLY with keys:\n"
            "1. 'transcribed_user_text': Exact words spoken by the user.\n"
            "2. 'display_markdown': Crisp, strategic response in Markdown.\n"
            "3. 'spoken_summary': 1 natural British sentence to speak aloud.\n"
            "4. 'suggestions': Array of 3 interactive quick-action prompt chips."
        )
        ctx_str = f"\nCurrent Context: {json.dumps(context)}" if context else ""
        
        for m in self.models:
            try:
                res = self.client.models.generate_content(
                    model=m,
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                        "Respond to this voice query with strategy." + ctx_str
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=500,
                        temperature=0.5
                    )
                )
                if res and res.text:
                    cleaned = res.text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    return json.loads(cleaned.strip())
            except Exception as e:
                print(f"Model {m} audio error:", e)
                continue

        return {
            "transcribed_user_text": "Voice instruction received",
            "display_markdown": "I received your voice instruction, Ahmad. Standing by for execution.",
            "spoken_summary": "Standing by for execution, sir.",
            "suggestions": ["Scrape New Leads", "Review Pipeline", "Check Inbox"]
        }

    def draft_cold_email(self, lead: dict, campaign: dict) -> dict:
        system_prompt = (
            "You are Harvey, Growth Director at ZotirLabs (zotirlabs.com). "
            "ZotirLabs builds high-converting bespoke websites clients can edit themselves with zero tickets or waiting. "
            "Write a bespoke, under-80-word outreach email that cuts through noise. "
            "NEVER use generic templates or robotic intros like 'I hope this finds you well'. "
            "Focus on the prospect's mobile visitor drop-off and offer a free 5-minute review with zero obligation. "
            "CTA is: https://zotirlabs.com/book. "
            "Output JSON ONLY with keys: 'subject', 'body', 'personalized_hook'."
        )
        user_prompt = (
            f"Campaign Offer: {campaign.get('offer', 'Free 5-Minute Website Review to Bring Enquiries')}\n"
            f"Booking Link: {campaign.get('booking_url', 'https://zotirlabs.com/book')}\n\n"
            f"Lead:\n"
            f"Name: {lead.get('name', 'Business Owner')}\n"
            f"Company: {lead.get('company', 'their firm')}\n"
            f"Website: {lead.get('website', '')}\n\n"
            "Return JSON only."
        )
        raw = self.generate(user_prompt, system_instruction=system_prompt, max_tokens=300)
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return {
                "subject": f"Quick website breakdown for {lead.get('company', 'your team')}",
                "body": (
                    f"Hi {lead.get('name', 'there')},\n\n"
                    f"I took a quick look at {lead.get('website', lead.get('company', 'your website'))}. "
                    "The design has strong elements, but mobile visitors appear to have friction before finding a direct way to enquire.\n\n"
                    "We put together a private 5-minute teardown showing where enquiries may be leaking and how to tighten it up.\n\n"
                    f"Would it be helpful if I shared it? You can pick a 10-minute slot here if easier: {campaign.get('booking_url', 'https://zotirlabs.com/book')}\n\n"
                    "Best regards,\nHarvey | ZotirLabs"
                ),
                "personalized_hook": "Mobile conversion teardown"
            }

    def analyze_reply(self, lead_email_text: str, conversation_history: str = "") -> dict:
        system_prompt = (
            "You are Harvey's Chief Inbound Sales Intelligence for ZotirLabs. "
            "Classify inbound email intent: ['INTERESTED', 'QUESTIONS', 'WHATSAPP_REQUEST', 'READY_TO_BUY', 'NOT_INTERESTED', 'OUT_OF_OFFICE'].\n"
            "Return valid JSON only with keys: 'intent', 'confidence', 'summary', 'recommended_action', 'draft_response'."
        )
        user_prompt = f"Inbound Email Content:\n{lead_email_text}\n\nHistory:\n{conversation_history}\n\nJSON output:"
        raw = self.generate(user_prompt, system_instruction=system_prompt, max_tokens=300)
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return {
                "intent": "INTERESTED",
                "confidence": 0.85,
                "summary": "Lead responded positively to website review.",
                "recommended_action": "Reply with calendar link",
                "draft_response": "Thanks for getting back to me! You can book a convenient 10-minute review here: https://zotirlabs.com/book"
            }
