import importlib.util
import os
import json
import time
import logging
from typing import Dict, Any, List
from highrise import User


def get_user_permissions(user: User) -> List[str]:
    """Retrieve permissions for a given user from the permissions config."""
    with open("config/permissions.json", "r") as f:
        data = json.load(f)
    user_permissions = []
    for permission in data["permissions"]:
        if permission["username"] == user.username:
            user_permissions = permission["permissions"]
            break
    return user_permissions


class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.commands: Dict[str, Any] = {}
        self.cooldowns: Dict[str, Dict[str, float]] = {}
        self.load_commands()

    def load_commands(self):
        """Load commands from modules in the src/commands directory."""
        commands_dir = os.path.join(os.path.dirname(__file__), "..", "commands")
        for category in os.listdir(commands_dir):
            category_dir = os.path.join(commands_dir, category)
            if os.path.isdir(category_dir):
                for command_file in os.listdir(category_dir):
                    if command_file.endswith(".py"):
                        command_name = os.path.splitext(command_file)[0]
                        command_module = f"src.commands.{category}.{command_name}"
                        spec = importlib.util.spec_from_file_location(
                            command_module, os.path.join(category_dir, command_file)
                        )
                        module = importlib.util.module_from_spec(spec)
                        try:
                            spec.loader.exec_module(module)
                            command = getattr(module, "Command")(self.bot)
                            if command_name in self.commands:
                                del self.commands[command_name]
                            for alias in getattr(command, "aliases", []):
                                if alias in self.commands:
                                    del self.commands[alias]
                            self.commands[command.name] = command
                            for alias in getattr(command, "aliases", []):
                                self.commands[alias] = command
                            logging.info(f"Loaded command: {command.name} (aliases: {getattr(command, 'aliases', [])})")
                        except Exception as e:
                            logging.error(f"Failed to load command {command_name}: {e}")

    async def handle_command(self, user: User, message: str):
        """Handle a chat message that starts with the prefix (e.g., /)."""
        parts = message[1:].split()
        if not parts:
            return
        command_name = parts[0]
        args = parts[1:]
        command = self.commands.get(command_name)
        if command:
            try:
                if hasattr(command, "permissions"):
                    user_permissions = get_user_permissions(user)
                    if not all(p in user_permissions for p in command.permissions):
                        await self.bot.highrise.send_whisper(user.id, "You don't have permissions to use this command")
                        logging.warning(f"Permission denied for user {user.username} on command {command_name}")
                        return
                cooldown = command.cooldown
                user_id = user.id
                if command_name in self.cooldowns and user_id in self.cooldowns[command_name]:
                    remaining_time = self.cooldowns[command_name][user_id] - time.time()
                    if remaining_time > 0:
                        await self.bot.highrise.send_whisper(user_id, f"{command_name} is on cooldown. Try again in {int(remaining_time)} seconds.")
                        return
                if command_name not in self.cooldowns:
                    self.cooldowns[command_name] = {}
                self.cooldowns[command_name][user_id] = time.time() + cooldown
                await command.execute(user, args, message)
            except Exception as e:
                await self.bot.highrise.send_whisper(user.id, "An error occurred while executing the command.")
                logging.error(f"Error executing command {command_name}: {e}")
