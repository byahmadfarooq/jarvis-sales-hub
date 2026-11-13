@echo off
title JARVIS // ZotirLabs Sales & Operations Hub
cd /d "D:\jarvis-sales-hub"
echo ===================================================
echo Starting Jarvis AI Executive Hub...
echo ===================================================
"C:\Users\ahmad\.local\bin\uv.exe" run --with fastapi --with uvicorn --with pydantic --with google-genai --with edge-tts --with httpx --with beautifulsoup4 python start_server.py
pause
