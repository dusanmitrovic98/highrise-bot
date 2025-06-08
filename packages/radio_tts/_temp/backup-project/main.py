import asyncio
# Import the TTS and radio server modules from the current package
from . import tts
from . import radio_server
import threading
# Import configuration values for port and TTS voice
from .config import PORT, TTS_VOICE

# Function to start the radio server in a separate thread
def start_radio_server():
    print(f"[DEBUG] Starting radio server thread on port {PORT}")
    # Start the radio server as a daemon thread so it doesn't block the main thread
    threading.Thread(target=radio_server.run_server, args=(PORT,), daemon=True).start()
    print("[DEBUG] Radio server thread started.")

# Function to convert text to speech and play it on the radio server
def say_on_radio(text):
    print(f"[DEBUG] say_on_radio called with text: {text}")
    # Define an async function to handle TTS and audio update
    async def _run():
        print(f"[DEBUG] _run: Generating TTS for: {text}")
        # Generate TTS audio file from text
        audio_path = await tts.text_to_speech(text, TTS_VOICE)
        print(f"[DEBUG] _run: TTS audio generated at: {audio_path}")
        # Set the new audio file for the radio server to stream
        radio_server.set_new_audio(audio_path)
        print(f"[DEBUG] _run: set_new_audio called with: {audio_path}")
    try:
        # Try to get the current running event loop (if inside an async context)
        loop = asyncio.get_running_loop()
        print("[DEBUG] Async event loop found, scheduling _run task.")
        # Schedule the async TTS and audio update task
        loop.create_task(_run())
    except RuntimeError:
        print("[DEBUG] No running event loop, running _run directly.")
        # If not in an async context, run the async function directly
        asyncio.run(_run())

# If this script is run directly, start the radio server and accept user input
if __name__ == "__main__":
    start_radio_server()
    print(f"Radio TTS server running on port {PORT}")
    # Loop to accept user input and play it on the radio
    while True:
        text = input("Text to say on radio: ")
        print(f"[DEBUG] User input: {text}")
        say_on_radio(text)
