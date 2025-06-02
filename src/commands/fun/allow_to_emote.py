import asyncio
import json
import random
from highrise import User
from config.config import config
from src.utility.ai import ask_bot
from src.commands.fun.emote import Command

class Command:
    def __init__(self, bot):
        self.bot = bot
        self.name = "allow_to_emote"
        self.description = "Allows the bot to emote."
        self.permissions = ["allow_to_emote"]
        self.aliases = ['speak', 'talk']
        self.cooldown = 10

    async def execute(self, user: User, args: list, message: str):
        prefix = config.prefix
        command = message.replace(f"{prefix}allow_to_emote", "").strip()

        if command == "yes":
            config.allowed_to_emote = True
            await ask_bot(self.bot, user, "I just allowed you to emote freely what do u say on that?")
        elif command == "no":
            config.allowed_to_emote = False
            await ask_bot(self.bot, user, "I just forbid you to emote freely what do u say on that?")

        # emotes_file = 'config/json/emotes.json'
        # with open(emotes_file) as f:
        #     emotes = json.load(f)
    
        # emote_name = random.choice(emotes)
        # command = Command(self.bot)
        # await command.execute(User(config.botID, "SebastianTheButler"), [emote_name], "")
        # while config.allowed_to_emote is True:
        #     await asyncio.sleep(random.uniform(2, 3))

        #     emote_name = random.choice(emotes)
        #     command = Command(self.bot)
        #     await command.execute(User(config.botID, "SebastianTheButler"), [emote_name], "")
            