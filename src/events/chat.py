import random
import json
from highrise.models import User
from config.config import loggers, config
from src.utility.ai import ask_bot
import logging

EMOTES_PATH = 'config/json/emotes.json'

def load_emotes():
    with open(EMOTES_PATH, 'r') as f:
        return set(json.load(f))

emote_names = load_emotes()

async def on_chat(bot, user: User, message: str) -> None:
    try:
        if loggers.messages:
            logging.info(f"(chat) {user.username}: {message}")
        if message.startswith("/ask"):
            pass
        else:
            if random.random() < 0.3:
                await ask_bot(bot, user, "\"" + message + "\"")
            pass
        if message.lstrip().startswith(config.prefix):
            await bot.command_handler.handle_command(user, message)

        # Play emote if message matches emote name
        msg = message.strip()
        if msg in emote_names:
            try:
                await bot.highrise.send_emote(msg, user.id)
            except Exception:
                await bot.highrise.send_whisper(user.id, f"Could not play emote '{msg}': emote not owned or not free.")
    except Exception as e:
        logging.error(f"Error in on_chat: {e}", exc_info=True)
