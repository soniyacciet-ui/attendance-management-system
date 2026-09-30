"""
AI voice generator using Edge TTS (Microsoft).
Free, no API key, supports 10+ Indian languages.
"""

import edge_tts
import asyncio
import os
from pathlib import Path
from django.conf import settings


# Language → Indian neural voice mapping
VOICES = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "ml": "ml-IN-SobhanaNeural",
    "kn": "kn-IN-SapnaNeural",
    "mr": "mr-IN-AarohiNeural",
    "bn": "bn-IN-TanishaaNeural",
    "gu": "gu-IN-DhwaniNeural",
    "pa": "pa-IN-GurpreetNeural",
}


def generate_voice(text, language, filename):
    """
    Generate an MP3 voice file from text using AI TTS.
    
    Args:
        text: The message text (in the target language)
        language: Language code (en, hi, ta, te, ml, kn, mr, bn, gu, pa)
        filename: Output filename (without path)
    
    Returns:
        Full path to generated MP3, or None on failure
    """
    # Ensure media folder exists
    media_dir = Path(settings.MEDIA_ROOT) / "voice"
    media_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = media_dir / filename
    voice = VOICES.get(language, VOICES["en"])

    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

    try:
        asyncio.run(_generate())
        return str(output_path)
    except Exception as e:
        print(f"[voice] Generation failed: {e}")
        return None