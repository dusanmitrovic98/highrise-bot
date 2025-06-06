import logging
from highrise.models import User, SessionMetadata, CurrencyItem, Item, Reaction, AnchorPosition, Position
from src.events import join, leave, emote, whisper, start, chat, tips, react, movement, message, before_start

async def handle_start(bot, session_metadata: SessionMetadata) -> None:
    try:
        await start.on_start(bot, session_metadata)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_start: {e}")


async def handle_join(bot, user: User) -> None:
    try:
        await join.on_join(bot, user)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_join: {e}")


async def handle_leave(bot, user: User) -> None:
    try:
        await leave.on_leave(bot, user)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_leave: {e}")


async def handle_whisper(bot, user: User, message: str) -> None:
    try:
        await whisper.on_whisper(bot, user, message)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_whisper: {e}")


async def handle_chat(bot, user: User, message: str) -> None:
    try:
        await chat.on_chat(bot, user, message)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_chat: {e}")


async def handle_emote(bot, user: User, emote_id: str, receiver: User) -> None:
    try:
        await emote.on_emote(bot, user, emote_id, receiver)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_emote: {e}")


async def handle_reactions(bot, user: User, reaction: Reaction, receiver: User) -> None:
    try:
        await react.on_reaction(bot, user, reaction, receiver)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_reactions: {e}")


async def handle_movements(bot, user: User, destination: Position | AnchorPosition) -> None:
    try:
        await movement.on_move(bot, user, destination)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_movements: {e}")


async def handle_tips(bot, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
    try:
        await tips.on_tip(bot, sender, receiver, tip)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_tips: {e}")


async def handle_message(bot, user_id: str, conversation_id: str, is_new_conversation: bool) -> None:
    try:
        await message.on_message(bot, user_id, conversation_id, is_new_conversation)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_message: {e}")


async def handle_before_start(bot, tg) -> None:
    try:
        await before_start.before_start(bot, tg)
    except Exception as e:
        logging.error(f"An Error Occurred in handle_before_start: {e}")
