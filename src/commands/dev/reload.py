import logging
from highrise import User
from src.commands.command_base import CommandBase

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        try:
            self.bot.command_handler.load_commands()
            await self.bot.highrise.send_whisper(user.id, "Commands and plugins reloaded successfully.")
            logging.info(f"{user.username} reloaded all commands and plugins.")
        except Exception as e:
            await self.bot.highrise.send_whisper(user.id, f"Reload failed: {e}")
            logging.error(f"Reload failed: {e}")
