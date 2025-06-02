import random
import json
from highrise import User
from config.config import config

COMMAND_NAME = "emote"
DESCRIPTION = "Perform a random emote on a specific player or all players in the room"
PERMISSIONS = ['emote']
COOLDOWN = 5
EMOTES_FILE = 'config/json/emotes.json'
DEFAULT_USERNAME = 'Hr.BotHelper'

class Command:
    """
    Command to perform a random emote on a specific player or all players in the room.
    """
    def __init__(self, bot):
        """
        Initialize the command with the bot instance.
        """
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = DESCRIPTION
        self.permissions = PERMISSIONS
        self.cooldown = COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command to perform a random emote.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        prefix = config.prefix
        emotes = self.load_emotes()

        if len(args) > 0:
            response = await self.bot.highrise.get_room_users()
            users = [content[0] for content in response.content]

            if args[0] == 'all':
                await self.emote_all(users, emotes)
                return

            target_username = args[0].lower()
            if not target_username:
                target_username = DEFAULT_USERNAME.lower()
            elif target_username.startswith('@'):
                target_username = target_username[1:]

            target_user = next((user for user in users if user.username.lower() == target_username.lower()), None)
            if not target_user:
                await self.bot.highrise.send_whisper(user.id, f"User '{target_username}' not found in the room.")
                return

            target_user_id = target_user.id
        else:
            target_username = user.username.lower()
            target_user_id = user.id

        emote_name = random.choice(emotes)
        await self.bot.highrise.send_emote(emote_name, target_user_id)

    def load_emotes(self):
        """
        Load the list of emotes from the JSON file.
        
        :return: List of emotes.
        """
        try:
            with open(EMOTES_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Emotes file {EMOTES_FILE} not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {EMOTES_FILE}.")
            return []

    async def emote_all(self, users, emotes):
        """
        Perform a random emote on all users in the room.
        
        :param users: List of users in the room.
        :param emotes: List of emotes.
        """
        for target_user in users:
            target_user_id = target_user.id
            emote_name = random.choice(emotes)
            await self.bot.highrise.send_emote(emote_name, target_user_id)
