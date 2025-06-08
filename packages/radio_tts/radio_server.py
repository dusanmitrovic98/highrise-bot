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
# Path to a background audio file to loop when no TTS is available
BACKGROUND_AUDIO = os.path.join(os.path.dirname(__file__), "background.mp3")

# Helper to stream an audio file in chunks
def stream_file(response, file_path):
    with open(file_path, 'rb') as f:
        chunk = f.read(4096)
        while chunk:
            yield chunk
            chunk = f.read(4096)

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
        while True:
            # If new TTS audio is available, stream it
            if current_audio and os.path.exists(current_audio) and current_audio != last_played:
                print(f"[DEBUG] Streaming new audio: {current_audio}")
                async for chunk in _async_stream_file(current_audio):
                    await response.write(chunk)
                last_played = current_audio
                # Delete the TTS file after playing
                try:
                    os.remove(current_audio)
                    print(f"[DEBUG] Deleted played TTS file: {current_audio}")
                except Exception as e:
                    print(f"[DEBUG] Failed to delete TTS file: {e}")
                current_audio = None
            else:
                # Loop background audio until interrupted by new TTS
                if os.path.exists(BACKGROUND_AUDIO):
                    with open(BACKGROUND_AUDIO, 'rb') as f:
                        while True:
                            chunk = f.read(4096)
                            if not chunk:
                                f.seek(0)  # Loop to start
                                continue
                            await response.write(chunk)
                            # Wait for either a short time or the event, for instant TTS interrupt
                            done, _ = await asyncio.wait([new_audio_event.wait()], timeout=0.05)
                            if new_audio_event.is_set() or (current_audio and os.path.exists(current_audio) and current_audio != last_played):
                                new_audio_event.clear()
                                break
                else:
                    # Stream silence if no background audio
                    await response.write(b'\0' * 4096)
                    await asyncio.sleep(0.1)
    except (asyncio.CancelledError, ConnectionResetError, Exception) as e:
        # Handle client disconnect or other exceptions gracefully
        print(f"[DEBUG] Exception or disconnect in stream_audio: {type(e).__name__}: {e}")
    print("[DEBUG] Exiting stream_audio handler.")
    return response

# Helper to stream a file asynchronously in chunks
def _async_stream_file(file_path, max_bytes=None):
    async def generator():
        with open(file_path, 'rb') as f:
            total = 0
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                yield chunk
                total += len(chunk)
                if max_bytes and total >= max_bytes:
                    break
    return generator()

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

# Periodic cleanup of old TTS files (older than 1 hour)
async def cleanup_audio_cache():
    while True:
        now = asyncio.get_event_loop().time()
        for file in glob.glob(os.path.join(AUDIO_DIR, 'tts_*.mp3')):
            try:
                if os.path.getmtime(file) < now - 3600:
                    os.remove(file)
                    print(f"[DEBUG] Cleaned up old TTS file: {file}")
            except Exception as e:
                print(f"[DEBUG] Cleanup error: {e}")
        await asyncio.sleep(1800)  # Run every 30 minutes

# Function to run the radio server on the specified port
def run_server(port=5002):
    print(f"[DEBUG] Starting radio server on port http://localhost:{port}/stream...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(cleanup_audio_cache())
    web.run_app(app, port=port)
