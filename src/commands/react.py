from highrise import User
from src.commands.command_base import CommandBase
import asyncio

REACTIONS = ["clap", "heart", "thumbs", "wave", "wink"]

class Command(CommandBase):
    name = "react"
    description = "Send a reaction to a user or all users in the room. Usage: !react <reaction> @user [count] [interval=seconds] or !react <reaction> all [count] [interval=seconds]. Supported reactions: clap, heart, thumbs, wave, wink."
    aliases = []
    cooldown = 0
    permissions = []

    async def execute(self, user: User, args: list, message: str):
        if not args or args[0] not in REACTIONS:
            await self.bot.highrise.chat(f"Usage: !react <reaction> @user [count] [interval=seconds] or !react <reaction> all [count] [interval=seconds]. Supported: {', '.join(REACTIONS)}")
            return
        reaction = args[0]
        count = 1
        interval = 0.3
        # Parse interval=... anywhere in args
        interval_args = [a for a in args if a.startswith("interval=")]
        if interval_args:
            try:
                interval = float(interval_args[0].split("=", 1)[1])
            except Exception:
                interval = 0.3
            args = [a for a in args if not a.startswith("interval=")]
        # Parse count if present (last arg and isdigit)
        if len(args) > 2 and args[-1].isdigit():
            count = int(args[-1])
            targets = args[1:-1]
        else:
            targets = args[1:]
        if not targets:
            for _ in range(count):
                await self.bot.highrise.react(reaction, user.id)
                await asyncio.sleep(interval)
            return
        if len(targets) == 1 and targets[0].lower() == "all":
            users_resp = await self.bot.highrise.get_room_users()
            if hasattr(users_resp, 'content'):
                for u, _ in users_resp.content:
                    if u.id != self.bot.highrise.my_id:
                        for _ in range(count):
                            await self.bot.highrise.react(reaction, u.id)
                            await asyncio.sleep(interval)
            return
        users_resp = await self.bot.highrise.get_room_users()
        if hasattr(users_resp, 'content'):
            usernames = [a[1:] for a in targets if a.startswith("@")]
            found = False
            for u, _ in users_resp.content:
                if u.username.lower() in [name.lower() for name in usernames]:
                    for _ in range(count):
                        await self.bot.highrise.react(reaction, u.id)
                        await asyncio.sleep(interval)
                    found = True
            if not found:
                await self.bot.highrise.chat("No specified users found in room.")
        else:
            await self.bot.highrise.chat(f"Usage: !react <reaction> @user [count] [interval=seconds] or !react <reaction> all [count] [interval=seconds]. Supported: {', '.join(REACTIONS)}")
