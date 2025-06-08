import asyncio
from aiohttp import web
import os
import glob
import webbrowser
import time
from mutagen.mp3 import MP3
from .config import BUFFER_SIZE
import subprocess

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
SILENCE_AUDIO = os.path.join(os.path.dirname(__file__), "silence.mp3")

# Track the global start time for background audio
background_start_time = time.time()
# Get the duration of the background audio (in seconds)
def get_mp3_duration(path):
    try:
        audio = MP3(path)
        return audio.info.length
    except Exception as e:
        print(f"[DEBUG] Could not get MP3 duration: {e}")
        return None
background_duration = get_mp3_duration(BACKGROUND_AUDIO) if os.path.exists(BACKGROUND_AUDIO) else None

# Helper to get byte offset for a given time offset in mp3 (approximate, CBR only)
def get_mp3_byte_offset(path, time_offset):
    try:
        audio = MP3(path)
        bitrate = audio.info.bitrate // 8  # bits to bytes per second
        return int(time_offset * bitrate)
    except Exception as e:
        print(f"[DEBUG] Could not get MP3 byte offset: {e}")
        return 0

# Helper to stream an audio file in chunks
def stream_file(response, file_path):
    with open(file_path, 'rb') as f:
        chunk = f.read(BUFFER_SIZE)
        while chunk:
            yield chunk
            chunk = f.read(BUFFER_SIZE)

# Helper to stream a file asynchronously in chunks
async def _async_stream_file(file_path, max_bytes=None):
    total = 0
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                yield chunk
                total += len(chunk)
                if max_bytes and total >= max_bytes:
                    break
    except Exception as e:
        print(f"[DEBUG] Error streaming file {file_path}: {e}")

# HTTP handler to stream audio to clients (professional streaming logic)
async def stream_audio(request):
    global current_audio
    print("[DEBUG] New client connected to /stream endpoint.")
    response = web.StreamResponse(status=200, reason='OK', headers={
        'Content-Type': 'audio/mpeg',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'icy-name': 'Highrise Radio',
        'icy-description': 'Live TTS & Background Radio',
    })
    await response.prepare(request)
    last_played = None
    try:
        while True:
            # Stream all available TTS files before returning to background
            while current_audio and os.path.exists(current_audio) and current_audio != last_played:
                print(f"[DEBUG] Streaming TTS audio: {current_audio}")
                async for chunk in _async_stream_file(current_audio):
                    await response.write(chunk)
                    await response.drain()
                last_played = current_audio
                try:
                    os.remove(current_audio)
                    print(f"[DEBUG] Deleted played TTS file: {current_audio}")
                except Exception as e:
                    print(f"[DEBUG] Failed to delete TTS file: {e}")
                current_audio = None
                new_audio_event.clear()
                # Check if another TTS file is available immediately
                await asyncio.sleep(0)  # Yield control to allow set_new_audio to run
            # If no TTS, play background audio
            bg_path = BACKGROUND_AUDIO if os.path.exists(BACKGROUND_AUDIO) else None
            if not bg_path or not background_duration:
                print("[DEBUG] No valid background audio, falling back to silence.mp3")
                bg_path = SILENCE_AUDIO if os.path.exists(SILENCE_AUDIO) else None
                if not bg_path:
                    print("[DEBUG] No silence.mp3 found. Nothing to stream.")
                    await asyncio.sleep(1)
                    continue
                bg_duration = get_mp3_duration(bg_path)
            else:
                bg_duration = background_duration
            print(f"[DEBUG] Streaming background audio: {bg_path}")
            while True:
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-hide_banner', '-loglevel', 'error',
                    '-i', bg_path,
                    '-f', 'mp3',
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-b:a', '128k',
                    '-'
                ]
                try:
                    ffmpeg_proc = await asyncio.create_subprocess_exec(
                        *ffmpeg_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    while True:
                        read_chunk_task = asyncio.create_task(ffmpeg_proc.stdout.read(BUFFER_SIZE))
                        wait_event_task = asyncio.create_task(new_audio_event.wait())
                        done, pending = await asyncio.wait(
                            [read_chunk_task, wait_event_task],
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        if read_chunk_task in done:
                            chunk = read_chunk_task.result()
                            if not chunk:
                                wait_event_task.cancel()
                                break
                            await response.write(chunk)
                            await response.drain()
                        if wait_event_task in done and new_audio_event.is_set() and current_audio and os.path.exists(current_audio) and current_audio != last_played:
                            print("[DEBUG] Interrupting background for TTS.")
                            read_chunk_task.cancel()
                            ffmpeg_proc.terminate()
                            await ffmpeg_proc.wait()
                            break
                        # Cancel any pending tasks to avoid warnings
                        for task in pending:
                            task.cancel()
                    await ffmpeg_proc.wait()
                    if new_audio_event.is_set() and current_audio and os.path.exists(current_audio) and current_audio != last_played:
                        break
                except Exception as e:
                    print(f"[DEBUG] ffmpeg streaming error: {e}")
                    await asyncio.sleep(1)
                # Loop background audio
                if not (new_audio_event.is_set() and current_audio and os.path.exists(current_audio) and current_audio != last_played):
                    print("[DEBUG] Looping background audio...")
                    continue
                break
    except (asyncio.CancelledError, ConnectionResetError) as e:
        print(f"[DEBUG] Client disconnected: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"[DEBUG] Exception in stream_audio: {type(e).__name__}: {e}")
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
    # Open the streaming page in the default browser
    webbrowser.open(f"http://localhost:{port}/stream")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(cleanup_audio_cache())
    web.run_app(app, port=port)
