import asyncio
import base64
from pathlib import Path
import edge_tts

import os

VOICE = "en-GB-RyanNeural"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path("/tmp/data") if os.environ.get("VERCEL") else BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class VoiceEngine:
    def __init__(self, voice: str = VOICE):
        self.voice = voice

    async def text_to_speech_file(self, text: str, output_path: str = None) -> str:
        if not output_path:
            output_path = str(DATA_DIR / "temp_response.mp3")
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        return output_path

    async def text_to_speech_base64(self, text: str) -> str:
        file_path = str(DATA_DIR / "speech_stream.mp3")
        await self.text_to_speech_file(text, file_path)
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return encoded

# Synchronous wrapper helper
def speak_sync(text: str) -> str:
    engine = VoiceEngine()
    return asyncio.run(engine.text_to_speech_base64(text))
