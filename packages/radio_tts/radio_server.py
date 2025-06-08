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
# Use an asyncio.Queue for TTS jobs
TTS_QUEUE = asyncio.Queue()
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

# Helper to stream a file asynchronously in chunks, transcoding to match stream format
async def _async_stream_file_ffmpeg(file_path, max_bytes=None):
    ffmpeg_cmd = [
        'ffmpeg',
        '-hide_banner', '-loglevel', 'error',
        '-i', file_path,
        '-f', 'mp3',
        '-vn',
        '-acodec', 'libmp3lame',
        '-b:a', '128k',
        '-'
    ]
    proc = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    total = 0
    try:
        while True:
            chunk = await proc.stdout.read(BUFFER_SIZE)
            if not chunk:
                break
            yield chunk
            total += len(chunk)
            if max_bytes and total >= max_bytes:
                break
    finally:
        proc.terminate()
        await proc.wait()

# HTTP handler to stream audio to clients (professional streaming logic)
async def stream_audio(request):
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
            # Try to get a TTS job from the queue (non-blocking)
            try:
                tts_path = TTS_QUEUE.get_nowait()
                print(f"[DEBUG] Got TTS job from queue: {tts_path}")
                if os.path.exists(tts_path):
                    print(f"[DEBUG] Streaming TTS audio: {tts_path}")
                    try:
                        async for chunk in _async_stream_file_ffmpeg(tts_path):
                            print(f"[DEBUG] Sending TTS chunk of size: {len(chunk)}")
                            await response.write(chunk)
                            await response.drain()
                        print(f"[DEBUG] Finished streaming TTS audio: {tts_path}")
                        last_played = tts_path
                    except Exception as e:
                        print(f"[DEBUG] Error streaming TTS file: {e}")
                    finally:
                        try:
                            os.remove(tts_path)
                            print(f"[DEBUG] Deleted played TTS file: {tts_path}")
                        except Exception as e:
                            print(f"[DEBUG] Failed to delete TTS file: {e}")
                else:
                    print(f"[DEBUG] TTS file does not exist: {tts_path}")
                continue  # After TTS, check for more TTS jobs
            except asyncio.QueueEmpty:
                pass  # No TTS jobs, play background
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
            # print(f"[DEBUG] Streaming background audio: {bg_path}")
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
                try:
                    while True:
                        read_chunk_task = asyncio.create_task(ffmpeg_proc.stdout.read(BUFFER_SIZE))
                        queue_wait_task = asyncio.create_task(TTS_QUEUE.get())
                        done, pending = await asyncio.wait(
                            [read_chunk_task, queue_wait_task],
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        if read_chunk_task in done:
                            chunk = read_chunk_task.result()
                            if not chunk:
                                queue_wait_task.cancel()
                                break
                            try:
                                await response.write(chunk)
                                await response.drain()
                            except (ConnectionResetError, asyncio.CancelledError):
                                print("[DEBUG] Client disconnected during background streaming.")
                                read_chunk_task.cancel()
                                queue_wait_task.cancel()
                                ffmpeg_proc.terminate()
                                await ffmpeg_proc.wait()
                                return response
                        if queue_wait_task in done:
                            # New TTS job arrived, put it back and break
                            tts_path = queue_wait_task.result()
                            print(f"[DEBUG] Interrupting background for TTS: {tts_path}")
                            read_chunk_task.cancel()
                            ffmpeg_proc.terminate()
                            await ffmpeg_proc.wait()
                            # Put the TTS job back for the next loop
                            await TTS_QUEUE.put(tts_path)
                            break
                        for task in pending:
                            task.cancel()
                    await ffmpeg_proc.wait()
                except (ConnectionResetError, asyncio.CancelledError):
                    print("[DEBUG] Client disconnected during background streaming (outer loop).")
                    ffmpeg_proc.terminate()
                    await ffmpeg_proc.wait()
                    return response
            except Exception as e:
                print(f"[DEBUG] ffmpeg streaming error: {e}")
                await asyncio.sleep(1)
    except (asyncio.CancelledError, ConnectionResetError) as e:
        print(f"[DEBUG] Client disconnected: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"[DEBUG] Exception in stream_audio: {type(e).__name__}: {e}")
    print("[DEBUG] Exiting stream_audio handler.")
    return response

# Function to set a new audio file for streaming and notify listeners
async def enqueue_tts(audio_path):
    print(f"[DEBUG] enqueue_tts called with: {audio_path}")
    await TTS_QUEUE.put(audio_path)
    print(f"[DEBUG] TTS job enqueued.")

def set_new_audio(audio_path):
    # For compatibility, keep this function, but use the queue
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(enqueue_tts(audio_path))
    else:
        loop.run_until_complete(enqueue_tts(audio_path))

# Create the aiohttp web application and add the /stream route
app = web.Application()
app.router.add_get('/stream', stream_audio)

# Graceful shutdown endpoint for the radio server
async def shutdown(request):
    print("[DEBUG] Shutdown endpoint called. Shutting down server gracefully.")
    await request.app.shutdown()
    await request.app.cleanup()
    asyncio.get_event_loop().call_later(0.5, asyncio.get_event_loop().stop)
    return web.Response(text="Server shutting down...")

app.router.add_post('/shutdown', shutdown)

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
        await asyncio.sleep(1800)  # Run every 1 minute

# Function to run the radio server on the specified port
def run_server(port=5002):
    print(f"[DEBUG] Starting radio server on port http://localhost:{port}/stream...")
    # Open the streaming page in the default browser
    webbrowser.open(f"http://localhost:{port}/stream")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(cleanup_audio_cache())
    web.run_app(app, port=port)

# HTTP endpoint to trigger TTS and play on radio
async def say_on_radio_endpoint(request):
    try:
        data = await request.json()
        text = data.get('text')
        print(f"[DEBUG] /say endpoint received text: {text}")
        if not text:
            print("[DEBUG] /say endpoint missing text!")
            return web.json_response({'error': 'Missing text'}, status=400)
        from . import tts
        audio_path = await tts.text_to_speech(text)
        print(f"[DEBUG] TTS audio_path generated: {audio_path}")
        print(f"[DEBUG] Does TTS file exist? {os.path.exists(audio_path)}")
        await enqueue_tts(audio_path)
        print(f"[DEBUG] enqueue_tts called from /say endpoint with: {audio_path}")
        return web.json_response({'status': 'ok', 'audio_path': audio_path})
    except Exception as e:
        print(f"[DEBUG] say_on_radio_endpoint error: {e}")
        return web.json_response({'error': str(e)}, status=500)

app.router.add_post('/say', say_on_radio_endpoint)
