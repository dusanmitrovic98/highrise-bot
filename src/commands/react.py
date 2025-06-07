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
        if not args:
            await self.bot.highrise.chat(f"Usage: !react <reaction(s)> @user [count] [interval=seconds] or !react <reaction(s)> all [count] [interval=seconds]. Supported: {', '.join(REACTIONS)}")
            return
        # Parse interval=... anywhere in args
        interval = 0.3
        interval_args = [a for a in args if a.startswith("interval=")]
        if interval_args:
            try:
                interval = float(interval_args[0].split("=", 1)[1])
            except Exception:
                interval = 0.3
            args = [a for a in args if not a.startswith("interval=")]
        # Parse count if present (last arg and isdigit)
        count = 1
        if len(args) > 1 and args[-1].isdigit():
            count = int(args[-1])
            args = args[:-1]
        # Find targets (all or @user)
        targets = []
        for i, a in enumerate(args):
            if a.lower() == "all" or a.startswith("@"):
                targets = args[i:]
                reactions = args[:i]
                break
        else:
            reactions = args
        # Validate reactions
        if not reactions or any(r not in REACTIONS for r in reactions):
            await self.bot.highrise.chat(f"Usage: !react <reaction(s)> @user [count] [interval=seconds] or !react <reaction(s)> all [count] [interval=seconds]. Supported: {', '.join(REACTIONS)}")
            return
        if not targets:
            # No target, react to self
            for i in range(count):
                for reaction in reactions:
                    await self.bot.highrise.react(reaction, user.id)
                    await asyncio.sleep(interval)
            return
        if len(targets) == 1 and targets[0].lower() == "all":
            users_resp = await self.bot.highrise.get_room_users()
            if hasattr(users_resp, 'content'):
                user_list = [u for u, _ in users_resp.content if u.id != self.bot.highrise.my_id]
                if not user_list:
                    return
                for i in range(count):
                    for idx, u in enumerate(user_list):
                        reaction = reactions[i % len(reactions)]
                        await self.bot.highrise.react(reaction, u.id)
                        await asyncio.sleep(interval)
            return
        users_resp = await self.bot.highrise.get_room_users()
        if hasattr(users_resp, 'content'):
            usernames = [a[1:] for a in targets if a.startswith("@")]
            user_list = [u for u, _ in users_resp.content if u.username.lower() in [name.lower() for name in usernames]]
            if not user_list:
                await self.bot.highrise.chat("No specified users found in room.")
                return
            for i in range(count):
                for idx, u in enumerate(user_list):
                    reaction = reactions[i % len(reactions)]
                    await self.bot.highrise.react(reaction, u.id)
                    await asyncio.sleep(interval)
        else:
            # Fallback usage message if users_resp has no content
            await self.bot.highrise.chat(f"Usage: !react <reaction(s)> @user [count] [interval=seconds] or !react <reaction(s)> all [count] [interval=seconds]. Supported: {', '.join(REACTIONS)}")
