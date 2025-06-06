import json
import logging
from pathlib import Path

from .dispatch_util import dispatch_event

USERS_PATH = Path("config/users.json")
PERMISSIONS_PATH = Path("config/permissions.json")

async def register_or_update_user(user_id, username):
    # Load users.json
    if USERS_PATH.exists():
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            users_data = json.load(f)
    else:
        users_data = {"users": {}}
    # Register or update user
    user_entry = users_data["users"].get(user_id, {})
    user_entry["username"] = username
    user_entry.setdefault("roles", ["guest"])
    user_entry.setdefault("extra_permissions", [])
    # Add more fields as needed
    users_data["users"][user_id] = user_entry
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users_data, f, indent=4)

    # Update permissions.json if not present
    if PERMISSIONS_PATH.exists():
        with open(PERMISSIONS_PATH, "r", encoding="utf-8") as f:
            perm_data = json.load(f)
    else:
        perm_data = {"users": {}, "roles": {}}
    if user_id not in perm_data["users"]:
        perm_data["users"][user_id] = {
            "username": username,
            "roles": ["guest"],
            "extra_permissions": []
        }
        with open(PERMISSIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(perm_data, f, indent=4)

async def handle_dm_subscribe(bot, user_id, username, conversation_id):
    await register_or_update_user(user_id, username)
    await bot.highrise.send_message(conversation_id, "Welcome! You are now subscribed. Your role is 'guest'.")

async def handle_dm_opening(bot, user_id, username, conversation_id):
    await register_or_update_user(user_id, username)
    await bot.highrise.send_message(conversation_id, "Hello! This is your first DM with the bot. You are now registered as a guest.")

async def on_message(bot, user_id: str, conversation_id: str, is_new_conversation: bool) -> None:
    logging.info(f"[DEBUG] on_message handler called: user_id={user_id}, conversation_id={conversation_id}, is_new={is_new_conversation}")
    # Try to get username from room users or fallback to user_id
    username = user_id
    try:
        users_resp = await bot.highrise.get_room_users()
        if hasattr(users_resp, 'content'):
            for user, _ in users_resp.content:
                if user.id == user_id:
                    username = user.username
                    break
    except Exception:
        pass
    # Register/update user on every DM
    await register_or_update_user(user_id, username)
    # Check for !subscribe command
    if hasattr(bot, 'last_dm_users'):
        last_dm_users = bot.last_dm_users
    else:
        last_dm_users = set()
        bot.last_dm_users = last_dm_users
    # Opening message if first DM
    if user_id not in last_dm_users:
        await handle_dm_opening(bot, user_id, username, conversation_id)
        last_dm_users.add(user_id)
        return
    # Handle !subscribe
    messages = await bot.highrise.get_messages(conversation_id)
    if hasattr(messages, "messages") and messages.messages:
        last_message = messages.messages[-1]
        if last_message.content.strip().lower() == "!subscribe":
            await handle_dm_subscribe(bot, user_id, username, conversation_id)
            return
    # Otherwise, normal DM log
        if hasattr(messages, "messages") and messages.messages:
            last_message = messages.messages[-1]
            logging.info(f"(dm) {user_id}: {last_message.content}")
    await dispatch_event(bot, "on_message", user_id, conversation_id, is_new_conversation)
