import os
import time
from collections import namedtuple
from pathlib import Path

from asyncio import run as arun
from dotenv import load_dotenv

from highrise import BaseBot
from highrise import __main__
from highrise.models import (
    AnchorPosition,
    CurrencyItem,
    Item,
    Position,
    Reaction,
    SessionMetadata,
    User,
)

from src.handlers.handleCommands import CommandHandler
from src.handlers.handleEvents import (
    handle_chat,
    handle_emote,
    handle_join,
    handle_leave,
    handle_movements,
    handle_reactions,
    handle_start,
    handle_tips,
    handle_whisper,
)


BotDefinition = namedtuple('BotDefinition', ['bot', 'room_id', 'api_token'])


class Bot(BaseBot):
    def __init__(self, room_id=None, token=None):
        self.command_handler = CommandHandler(self)
        self.room_id = room_id
        self.token = token
        super().__init__()

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        await handle_start(self, session_metadata)

    async def on_chat(self, user: User, message: str) -> None:
        await handle_chat(self, user, message)

    async def on_whisper(self, user: User, message: str) -> None:
        await handle_whisper(self, user, message)

    async def on_user_join(self, user: User, position: Position) -> None:
        await handle_join(self, user)

    async def on_user_leave(self, user: User) -> None:
        await handle_leave(self, user)

    async def on_emote(self, user: User, emote_id: str, receiver: User | None) -> None:
        await handle_emote(self, user, emote_id, receiver)

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        await handle_tips(self, sender, receiver, tip)

    async def on_reaction(self, user: User, reaction: Reaction, receiver: User) -> None:
        await handle_reactions(self, user, reaction, receiver)

    async def on_user_move(self, user: User, destination: Position | AnchorPosition) -> None:
        await handle_movements(self, user, destination)

    @classmethod
    async def before_start(cls, tg):
        pass

    async def run(self, room_id, token):
        self.room_id = room_id
        self.token = token
        await __main__.main([self])


if __name__ == "__main__":
    load_dotenv()
    flag_path = Path("runtime/flags/warp.flag")
    room_id = os.getenv("ROOM_ID")
    token = os.getenv("TOKEN")
    # Check for warp.flag and use its value as room_id if present
    if flag_path.exists():
        portal_room_id = flag_path.read_text().strip()
        if portal_room_id:
            room_id = portal_room_id
        flag_path.unlink()  # Remove flag for next time
    shutdown_flag = Path("shutdown.flag")
    # Always remove shutdown flag on startup
    if shutdown_flag.exists():
        shutdown_flag.unlink()
    while True:
        if shutdown_flag.exists():
            print("Shutdown flag detected. Exiting bot loop.")
            break
        try:
            bot_def = BotDefinition(bot=Bot(room_id, token), room_id=room_id, api_token=token)
            arun(__main__.main([bot_def]))
        except Exception as e:
            print(f"Bot crashed with exception: {e}. Restarting in 5 seconds...")
            # time.sleep(5)
