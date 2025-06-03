import importlib.util
import os
import json
import time
import logging
from typing import Dict, Any, List
from highrise import User


def get_user_permissions(user: User) -> List[str]:
    """Retrieve permissions for a given user from the new roles-based permissions config."""
    with open("config/permissions.json", "r") as f:
        data = json.load(f)
    users = data.get("users", {})
    roles = data.get("roles", {})
    user_entry = users.get(user.id)
    permissions_set = set()
    if user_entry:
        for role in user_entry.get("roles", []):
            role_perms = roles.get(role, [])
            if "*" in role_perms:
                # Owner: all permissions, truly unrestricted
                return ["*"]
            permissions_set.update(role_perms)
        permissions_set.update(user_entry.get("extra_permissions", []))
        # Also add role names as permissions for admin/owner checks
        permissions_set.update(user_entry.get("roles", []))
    return list(permissions_set)


class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.commands: Dict[str, Any] = {}
        self.cooldowns: Dict[str, Dict[str, float]] = {}
        self.load_commands()

    def load_commands(self):
        """Load commands from modules in the src/commands directory and plugins directory, using config/commands.json for config."""
        # Load command config database
        commands_config = {}
        try:
            with open(os.path.join(os.path.dirname(__file__), "..", "..", "config", "commands.json"), "r", encoding="utf-8") as f:
                commands_config = json.load(f)
        except Exception as e:
            logging.warning(f"Could not load commands.json: {e}")
        self.commands_config = commands_config
        commands_dir = os.path.join(os.path.dirname(__file__), "..", "commands")
        self._load_commands_from_dir(commands_dir, module_prefix="src.commands")
        # Plugin loader: load from plugins/ directory if exists
        plugins_dir = os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
        if os.path.isdir(plugins_dir):
            self._load_commands_from_dir(plugins_dir, module_prefix="plugins", is_plugin=True)

    def _load_commands_from_dir(self, base_dir, module_prefix, is_plugin=False):
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if not file.endswith(".py"):
                    continue
                if file == "command_base.py":
                    continue  # Skip abstract base class
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                command_name = os.path.splitext(os.path.basename(file))[0]
                module_path = rel_path.replace(os.sep, ".")[:-3]  # remove .py
                command_module = f"{module_prefix}.{module_path}" if module_path else f"{module_prefix}.{command_name}"
                spec = importlib.util.spec_from_file_location(
                    command_module, os.path.join(root, file)
                )
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    if not hasattr(module, "Command"):
                        continue  # Skip files that do not define a Command class
                    command = getattr(module, "Command")(self.bot)
                    # Inject config from commands.json if present
                    config = self.commands_config.get(command_name)
                    if config:
                        for k, v in config.items():
                            setattr(command, k, v)
                    if command_name in self.commands:
                        del self.commands[command_name]
                    for alias in getattr(command, "aliases", []):
                        if alias in self.commands:
                            del self.commands[alias]
                    self.commands[command.name] = command
                    for alias in getattr(command, "aliases", []):
                        self.commands[alias] = command
                    if is_plugin:
                        logging.info(f"Loaded plugin command: {command.name} (aliases: {getattr(command, 'aliases', [])}) from {file}")
                    else:
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
                # Log command usage attempt
                logging.info(f"User '{user.username}' (ID: {user.id}) is attempting command '{command_name}' with args: {args}")
                if hasattr(command, "permissions"):
                    user_permissions = get_user_permissions(user)
                    # If command has no permissions, allow all users
                    if not command.permissions:
                        pass
                    elif "*" in user_permissions:
                        pass
                    elif command.permissions and not any(p in user_permissions for p in command.permissions):
                        await self.bot.highrise.send_whisper(user.id, f"You don't have permissions to use the '{command_name}' command. Required: {', '.join(command.permissions) or 'None'}.")
                        logging.warning(f"Permission denied for user {user.username} on command {command_name}")
                        return
                cooldown = command.cooldown
                user_id = user.id
                if command_name in self.cooldowns and user_id in self.cooldowns[command_name]:
                    remaining_time = self.cooldowns[command_name][user_id] - time.time()
                    if remaining_time > 0:
                        await self.bot.highrise.send_whisper(user_id, f"'{command_name}' is on cooldown. Try again in {int(remaining_time)} seconds.")
                        logging.info(f"User {user.username} tried to use '{command_name}' during cooldown.")
                        return
                if command_name not in self.cooldowns:
                    self.cooldowns[command_name] = {}
                self.cooldowns[command_name][user_id] = time.time() + cooldown
                await command.execute(user, args, message)
                logging.info(f"Command '{command_name}' executed successfully for user '{user.username}' (ID: {user.id})")
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                await self.bot.highrise.send_whisper(user.id, f"An error occurred while executing '{command_name}'. Please check your command usage or try again later.")
                logging.error(f"Error executing command '{command_name}' for user '{user.username}' (ID: {user.id}) with args {args}: {e}\n{tb}")

# Placeholder for future external logging (e.g., to a database or HTTP endpoint)
def log_to_external_service(event_type: str, data: dict):
    """
    Placeholder for logging command usage or errors to an external service.
    Implement this function to send logs to a database, analytics service, or HTTP endpoint.
    Args:
        event_type (str): The type of event (e.g., 'command_usage', 'command_error').
        data (dict): The event data to log.
    """
    pass
