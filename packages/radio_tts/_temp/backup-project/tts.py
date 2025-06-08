import asyncio
import edge_tts
import uuid
import os

# Default voice for TTS
VOICE = "en-US-AriaNeural"
# Directory to store generated audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_cache")
# Ensure the audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# Async function to convert text to speech and save as an audio file
async def text_to_speech(text, voice=VOICE):
    # Generate a unique filename for the audio file
    filename = os.path.join(AUDIO_DIR, f"tts_{uuid.uuid4()}.mp3")
    # Create an edge_tts Communicate object for TTS
    communicate = edge_tts.Communicate(text, voice)
    # Save the generated speech to the file
    await communicate.save(filename)
    # Return the path to the generated audio file
    return filename
