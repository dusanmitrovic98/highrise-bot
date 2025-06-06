import logging
from config.config import loggers
from highrise.models import User
from .dispatch_util import dispatch_event
# Add utility import for permissions
from src.utility.utility import load_permissions, save_permissions


async def on_join(bot, user: User) -> None:
    # --- Permissions auto-add logic ---
    data = load_permissions()
    if user.id not in data.get("users", {}):
        data["users"][user.id] = {
            "username": user.username,
            "roles": ["guest"],  # Set new users as 'guest'
            "extra_permissions": []
        }
        save_permissions(data)
    # --- End permissions logic ---
    await bot.highrise.chat(f"{user.username} Joined the room!")
    await dispatch_event(bot, "on_join", user)
