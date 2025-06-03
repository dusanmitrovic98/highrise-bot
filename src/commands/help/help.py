from highrise import User
from src.commands.command_base import CommandBase


class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        # now notice that we used self.bot.highrise and not self.highrise, keep this in mind
        await self.bot.highrise.chat('this is a help command')
        # now you can use this template for all commands just copy and paste it
        # i hope this helped !
