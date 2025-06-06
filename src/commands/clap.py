from highrise import User
from src.commands.command_base import CommandBase
import asyncio

class Command(CommandBase):
    name = "clap"
    description = "Send a clap reaction to one or more users, or all users in the room. Usage: !clap @user1 @user2 ... [count] [interval=seconds] | !clap all [count] [interval=seconds]"
    aliases = []
    cooldown = 0
    permissions = []

    async def execute(self, user: User, args: list, message: str):
        count = 1
        interval = 0.3
        interval_args = [a for a in args if a.startswith("interval=")]
        if interval_args:
            try:
                interval = float(interval_args[0].split("=", 1)[1])
            except Exception:
                interval = 0.3
            args = [a for a in args if not a.startswith("interval=")]
        if args and args[-1].isdigit():
            count = int(args[-1])
            targets = args[:-1]
        else:
            targets = args
        if not targets:
            for _ in range(count):
                await self.bot.highrise.react("clap", user.id)
                await asyncio.sleep(interval)
            return
        if len(targets) == 1 and targets[0].lower() == "all":
            users_resp = await self.bot.highrise.get_room_users()
            if hasattr(users_resp, 'content'):
                for u, _ in users_resp.content:
                    if u.id != self.bot.highrise.my_id:
                        for _ in range(count):
                            await self.bot.highrise.react("clap", u.id)
                            await asyncio.sleep(interval)
            return
        users_resp = await self.bot.highrise.get_room_users()
        if hasattr(users_resp, 'content'):
            usernames = [a[1:] for a in targets if a.startswith("@")]
            found = False
            for u, _ in users_resp.content:
                if u.username.lower() in [name.lower() for name in usernames]:
                    for _ in range(count):
                        await self.bot.highrise.react("clap", u.id)
                        await asyncio.sleep(interval)
                    found = True
            if not found:
                await self.bot.highrise.chat("No specified users found in room.")
        else:
            await self.bot.highrise.chat("Usage: !clap @user1 @user2 ... [count] [interval=seconds] | !clap all [count] [interval=seconds]")
