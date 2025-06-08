import asyncio
from aiohttp import web
import os
import glob

# Directory to store cached audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_cache")
# Path to the current audio file to be streamed
global current_audio
current_audio = None
# Event to signal when new audio is available
global new_audio_event
new_audio_event = asyncio.Event()

# HTTP handler to stream audio to clients
async def stream_audio(request):
    global current_audio
    print("[DEBUG] New client connected to /stream endpoint.")
    # Prepare a streaming HTTP response with appropriate headers
    response = web.StreamResponse(status=200, reason='OK', headers={
        'Content-Type': 'audio/mpeg',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    })
    await response.prepare(request)
    last_played = None
    try:
        # On client connect, play the latest audio if it exists
        print(f"[DEBUG] Checking if current_audio exists: {current_audio}")
        if current_audio and os.path.exists(current_audio):
            print(f"[DEBUG] Playing initial audio: {current_audio}")
            last_played = current_audio
            with open(current_audio, 'rb') as f:
                chunk = f.read(4096)
                while chunk:
                    await response.write(chunk)
                    chunk = f.read(4096)
            print(f"[DEBUG] Finished sending initial audio: {current_audio}")
        else:
            print("[DEBUG] No initial audio to play or file does not exist.")
        while True:
            # Wait for new audio to be set
            print("[DEBUG] Waiting for new audio event...")
            await new_audio_event.wait()
            print("[DEBUG] New audio event received.")
            new_audio_event.clear()
            # If new audio is available and different from last played, stream it
            print(f"[DEBUG] current_audio: {current_audio}, last_played: {last_played}")
            if current_audio and os.path.exists(current_audio) and current_audio != last_played:
                print(f"[DEBUG] Streaming new audio: {current_audio}")
                last_played = current_audio
                with open(current_audio, 'rb') as f:
                    chunk = f.read(4096)
                    while chunk:
                        await response.write(chunk)
                        chunk = f.read(4096)
                print(f"[DEBUG] Finished sending new audio: {current_audio}")
            else:
                print("[DEBUG] No new audio to stream or file does not exist.")
    except (asyncio.CancelledError, ConnectionResetError, Exception) as e:
        # Handle client disconnect or other exceptions gracefully
        print(f"[DEBUG] Exception or disconnect in stream_audio: {type(e).__name__}: {e}")
    print("[DEBUG] Exiting stream_audio handler.")
    return response

# Function to set a new audio file for streaming and notify listeners
def set_new_audio(audio_path):
    global current_audio
    print(f"[DEBUG] set_new_audio called with: {audio_path}")
    current_audio = audio_path
    # Signal that new audio is available
    new_audio_event.set()
    print("[DEBUG] new_audio_event set.")

# Create the aiohttp web application and add the /stream route
app = web.Application()
app.router.add_get('/stream', stream_audio)

# Function to run the radio server on the specified port
def run_server(port=5002):
    print(f"[DEBUG] Starting radio server on port http://localhost:{port}/stream...")
    web.run_app(app, port=port)
