from highrise.models import User
from .dispatch_util import dispatch_event
from src.utility.utility import load_users, save_users


async def on_join(bot, user: User) -> None:
    # --- User auto-add logic ---
    data = load_users()
    if user.id not in data.get("users", {}):
        data["users"][user.id] = {
            "username": user.username,
            "roles": ["guest"],  # Set new users as 'guest'
            "extra_permissions": []
        }
        save_users(data)
    # --- End user logic ---
    await bot.highrise.chat(f"{user.username} Joined the room!")
    await dispatch_event(bot, "on_join", user)
