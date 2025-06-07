import json
import asyncio
import logging

from pathlib import Path

from .dispatch_util import dispatch_event

USERS_PATH = Path("config/users.json")

async def on_message(
    bot, user_id: str, conversation_id: str, is_new_conversation: bool
) -> None:
    """
    Handles incoming messages, logs the last message, and manages user data.
    Refactored for clarity and efficiency.
    """
    await handle_last_message_and_user(bot, user_id, conversation_id)
    await dispatch_event(bot, "on_message", user_id, conversation_id, is_new_conversation)


def get_username_from_user_info(user_info):
    """
    Extract the username from a user_info object, handling both possible structures.
    """
    if hasattr(user_info, "user") and hasattr(user_info.user, "username"):
        return user_info.user.username
    return getattr(user_info, "username", None)


def modulate(value, min_value, max_value):
    """
    Clamp value between min_value and max_value.
    """
    return max(min_value, min(value, max_value))


def load_users_data():
    """
    Load users data from USERS_PATH, or return a default structure if not found.
    """
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}


def save_users_data(users_data):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users_data, f, indent=4)


async def ensure_user_in_data(bot, user_id: str, users_data: dict) -> None:
    """
    Ensure the user exists in users_data; if not, fetch and add them.
    """
    if user_id not in users_data["users"]:
        user_info = await bot.webapi.get_user(user_id)
        username = get_username_from_user_info(user_info)
        users_data["users"][user_id] = {
            "username": username,
            "roles": ["guest"],
            "extra_permissions": []
        }
        save_users_data(users_data)


async def fetch_last_message(bot, conversation_id: str):
    """
    Fetch the last message from a conversation.
    """
    messages_response = await bot.highrise.get_messages(conversation_id)
    messages = getattr(messages_response, "messages", [])
    if messages:
        return messages[0]
    return None


async def fetch_user_infos(bot, user_ids):
    """
    Fetch user info objects for a list of user IDs.
    """
    user_infos = await asyncio.gather(*(bot.webapi.get_user(uid) for uid in user_ids))
    return dict(zip(user_ids, user_infos))


def log_last_message(last_msg, user_id, user_info_map):
    """
    Log the last message with user label and username.
    """
    last_msg_user_info = user_info_map.get(last_msg.sender_id)
    last_msg_username = get_username_from_user_info(last_msg_user_info)
    user_label = "[USER]" if last_msg.sender_id == user_id else "[BOT ]"
    logging.info(f"[LAST MESSAGE] {user_label} [{last_msg_username}] {last_msg.content}")


def prepare_user_ids_to_fetch(user_id, last_msg):
    """
    Prepare a list of user IDs to fetch info for.
    """
    user_ids = [user_id]
    if last_msg.sender_id != user_id:
        user_ids.append(last_msg.sender_id)
    return user_ids


async def ensure_user_in_data_async(bot, user_id):
    """
    Load users data and ensure the user is present.
    """
    users_data = load_users_data()
    await ensure_user_in_data(bot, user_id, users_data)


async def handle_last_message_and_user(bot, user_id: str, conversation_id: str) -> None:
    """
    Fetches and logs the last message in a conversation and ensures the user is present in user data.
    """
    try:
        last_msg = await fetch_last_message(bot, conversation_id)
        if last_msg:
            user_ids_to_fetch = prepare_user_ids_to_fetch(user_id, last_msg)
            user_info_map = await fetch_user_infos(bot, user_ids_to_fetch)
            log_last_message(last_msg, user_id, user_info_map)
    except Exception as e:
        logging.error(f"Error fetching last message: {e}")
    await ensure_user_in_data_async(bot, user_id)
