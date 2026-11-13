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

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        if not self.client:
            return "Error: GEMINI_API_KEY is not configured in .env."
        
        last_error = None
        for m in self.models:
            try:
                config = types.GenerateContentConfig()
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
        """Executive conversational assistant returning BOTH markdown for display and a fluid spoken summary."""
        system_prompt = (
            "You are Jarvis, the charismatic, British, and ultra-competent executive AI co-pilot for Ahmad and Harvey at ZotirLabs (zotirlabs.com). "
            "You manage outreach, campaign strategy, document drafting, and business operations. "
            "CRITICAL: Always respond with valid JSON ONLY with two fields:\n"
            "1. 'display_markdown': The complete, detailed response using clean Markdown (bold **headers**, bullet points, clear spacing).\n"
            "2. 'spoken_summary': A natural, fluid, 1-to-2 sentence conversational summary written specifically for human speech. "
            "DO NOT put colons, bullet points, asterisks, or lists in 'spoken_summary'. It must read like an articulate British gentleman speaking naturally in one breath."
        )
        ctx_str = f"\nCurrent System Context: {json.dumps(context)}" if context else ""
        raw = self.generate(message + ctx_str, system_instruction=system_prompt)
        
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
                "spoken_summary": data.get("spoken_summary", "All systems are operational, sir. How may I assist you?")
            }
        except Exception:
            return {
                "display_markdown": raw,
                "spoken_summary": "Understood, sir. I have processed your request."
            }

    def process_voice_audio(self, audio_bytes: bytes, mime_type: str = "audio/webm", context: dict = None) -> dict:
        """Processes raw audio directly from the user's microphone, transcribes it, and responds."""
        system_prompt = (
            "You are Jarvis, executive AI co-pilot for ZotirLabs. "
            "Ahmad is speaking to you via microphone. Listen to his audio, transcribe what he said, and answer him. "
            "Return valid JSON ONLY with three fields:\n"
            "1. 'transcribed_user_text': The exact words spoken by the user.\n"
            "2. 'display_markdown': Your complete response in clear, beautiful Markdown.\n"
            "3. 'spoken_summary': 1-2 smooth sentences of natural British speech to reply back verbally (NO asterisks, NO bullets, NO colons)."
        )
        ctx_str = f"\nCurrent System Context: {json.dumps(context)}" if context else ""
        
        for m in self.models:
            try:
                res = self.client.models.generate_content(
                    model=m,
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                        "Respond to this voice query." + ctx_str
                    ],
                    config=types.GenerateContentConfig(system_instruction=system_prompt)
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
                print(f"Model {m} audio processing failed:", e)
                continue

        return {
            "transcribed_user_text": "Voice input received",
            "display_markdown": "I heard your voice command, sir, but encountered a processing delay. Please try again.",
            "spoken_summary": "I heard your voice command, sir. Please try speaking again."
        }

    def draft_cold_email(self, lead: dict, campaign: dict) -> dict:
        system_prompt = (
            "You are Harvey, Growth Director at ZotirLabs (zotirlabs.com). "
            "Your personality is sharp, British, professional, concise, and respectful of the prospect's time. "
            "ZotirLabs builds websites that bring enquiries, fast development, and clean CMS with zero waiting. "
            "The Call-To-Action (CTA) is to offer a 100% free, 5-minute website review at https://zotirlabs.com/book. "
            "Write cold emails that are under 100 words, direct, with no robotic buzzwords ('hope this email finds you well' is BANNED). "
            "Output valid JSON ONLY with keys: 'subject', 'body', 'personalized_hook'."
        )
        user_prompt = (
            f"Campaign Details:\n"
            f"Company: {campaign.get('company_name', 'ZotirLabs')}\n"
            f"Service/Offer: {campaign.get('offer', 'Free Website Review to bring enquiries')}\n"
            f"Booking Link: {campaign.get('booking_url', 'https://zotirlabs.com/book')}\n\n"
            f"Lead Details:\n"
            f"Name: {lead.get('name', 'Business Owner')}\n"
            f"Company: {lead.get('company', 'their company')}\n"
            f"Website: {lead.get('website', '')}\n"
            f"Notes/Industry: {lead.get('notes', '')}\n\n"
            "Return JSON only."
        )
        raw = self.generate(user_prompt, system_instruction=system_prompt)
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
                "subject": f"Quick website review for {lead.get('company', 'your team')}",
                "body": (
                    f"Hi {lead.get('name', 'there')},\n\n"
                    f"I took a look at {lead.get('website', lead.get('company', 'your site'))}. "
                    "Most agency sites look nice but struggle to convert mobile visitors into actual client enquiries.\n\n"
                    "We put together a free 5-minute breakdown showing where visitors might be dropping off before they reach out.\n\n"
                    f"Would it be helpful if I shared the review? You can pick a quick slot here if easier: {campaign.get('booking_url', 'https://zotirlabs.com/book')}\n\n"
                    "Best regards,\nHarvey | ZotirLabs"
                ),
                "personalized_hook": "Mobile conversion review"
            }

    def analyze_reply(self, lead_email_text: str, conversation_history: str = "") -> dict:
        system_prompt = (
            "You are Harvey's Chief Inbound Sales Intelligence for ZotirLabs. "
            "Analyze the client's reply and categorize their intent into one of: "
            "['INTERESTED', 'QUESTIONS', 'WHATSAPP_REQUEST', 'READY_TO_BUY', 'NOT_INTERESTED', 'OUT_OF_OFFICE'].\n"
            "Return valid JSON only with keys: 'intent', 'confidence', 'summary', 'recommended_action', 'draft_response'."
        )
        user_prompt = f"Inbound Email Content:\n{lead_email_text}\n\nHistory:\n{conversation_history}\n\nJSON output:"
        raw = self.generate(user_prompt, system_instruction=system_prompt)
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
                "confidence": 0.8,
                "summary": "Lead responded to outreach.",
                "recommended_action": "Reply with booking link",
                "draft_response": "Thank you for getting back to me! You can pick a convenient 15-minute time here: https://zotirlabs.com/book"
            }
