import requests
from src.commands.command_base import CommandBase

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user, args, message):
        try:
            if not args:
                await self.bot.highrise.send_whisper(user.id, "Usage: !tts [list [start]|use <number>]")
                return

            tts_url_voices = self.get_setting("tts_url_voices", "http://localhost:5002/voices")
            tts_url_use = self.get_setting("tts_url_use", "http://localhost:5002/use")

            if args[0] == "list":
                try:
                    page = 1
                    if len(args) > 1 and args[1].isdigit():
                        page = int(args[1])
                    voices_resp = requests.get(tts_url_voices)
                    voices = voices_resp.json()
                    total = len(voices)
                    keys = sorted(list(voices.keys()))  # Sort keys for consistent order
                    per_page = 5
                    start_idx = (page - 1) * per_page
                    if start_idx < 0 or start_idx >= total:
                        await self.bot.highrise.send_whisper(user.id, f"Page must be between 1 and {((total-1)//per_page)+1}.")
                        return
                    end_idx = min(start_idx + per_page, total)
                    msg = f"Total voices: {total}\n"
                    for idx in range(start_idx, end_idx):
                        v = keys[idx]
                        msg += f"{idx+1}: {v}\n"
                        if (idx - start_idx + 1) % 6 == 0 and idx + 1 < end_idx:
                            msg += "\n"
                    if end_idx < total:
                        msg += f"... (use !tts list {page+1} for more)"
                    await self.bot.highrise.send_whisper(user.id, msg)
                except Exception as e:
                    await self.bot.highrise.send_whisper(user.id, f"Failed to fetch voices: {e}")
                return

            if args[0] == "use" and len(args) == 2 and args[1].isdigit():
                try:
                    number = int(args[1])
                    voices_resp = requests.get(tts_url_voices)
                    voices = voices_resp.json()
                    total = len(voices)
                    keys = sorted(list(voices.keys()))  # Sort keys for consistent order
                    if number < 1 or number > total:
                        await self.bot.highrise.send_whisper(user.id, f"Voice number must be between 1 and {total}.")
                        return
                    voice_key = keys[number - 1]
                    use_resp = requests.post(f"{tts_url_use}/{number}")
                    await self.bot.highrise.send_whisper(user.id, f"Set voice response: {{'status': 'ok', 'voice': '{voice_key}'}}")
                except Exception as e:
                    await self.bot.highrise.send_whisper(user.id, f"Failed to set voice: {e}")
                return

            if args[0] == "filter" and len(args) > 1:
                try:
                    filter_text = " ".join(args[1:]).lower()
                    page = 1
                    # Check if the last argument is a digit (page number)
                    if args[-1].isdigit() and len(args) > 2:
                        page = int(args[-1])
                        filter_text = " ".join(args[1:-1]).lower()
                    voices_resp = requests.get(tts_url_voices)
                    voices = voices_resp.json()
                    keys = sorted(list(voices.keys()))
                    matches = []
                    for idx, v in enumerate(keys):
                        if filter_text in v.lower():
                            matches.append((idx + 1, v))
                    per_page = 5
                    start_idx = (page - 1) * per_page
                    end_idx = start_idx + per_page
                    page_matches = matches[start_idx:end_idx]
                    if page_matches:
                        msg = f"Matches (page {page}):\n"
                        for idx, v in page_matches:
                            msg += f"{idx}: {v}\n"
                            if (page_matches.index((idx, v)) + 1) % 6 == 0 and (page_matches.index((idx, v)) + 1) < len(page_matches):
                                msg += "\n"
                        if end_idx < len(matches):
                            msg += f"... (use !tts filter {filter_text} {page+1} for more)"
                    else:
                        msg = "No voices found matching that text."
                    await self.bot.highrise.send_whisper(user.id, msg)
                except Exception as e:
                    await self.bot.highrise.send_whisper(user.id, f"Failed to filter voices: {e}")
                return

            await self.bot.highrise.send_whisper(user.id, "Usage: !tts [list [start]|use <number>]")
        except Exception as e:
            await self.bot.highrise.send_whisper(user.id, f"Failed to process TTS command: {e}")
