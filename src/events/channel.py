import logging

from .dispatch_util import dispatch_event


async def on_channel(bot, sender_id: str, message: str, tags: set[str]) -> None:
    """
    Handle hidden channel messages (on_channel event).
    :param bot: The bot instance.
    :param sender_id: The ID of the sender.
    :param message: The message sent on the channel.
    :param tags: The set of tags associated with the message.
    """
    logging.info(f"[CHANNEL] {sender_id}: {message} (tags: {tags})")
    # Example: respond to a special admin tag
    if 'admin' in tags:
        await bot.highrise.chat(f"[ADMIN CHANNEL] Message from {sender_id}: {message}")
    # Real-life use case: trigger a silent giveaway for users with a 'giveaway' tag
    if 'giveaway' in tags:
        # This could trigger a giveaway logic, e.g., enter sender_id into a giveaway pool
        # For demo, just acknowledge silently (no public chat)
        logging.info(f"[GIVEAWAY] {sender_id} entered the giveaway via channel message.")
        # Optionally, send a private whisper to the user
        await bot.highrise.send_whisper(sender_id, "You have been entered into the giveaway!")
    # Dispatch to all plugin/command on_channel handlers
    await dispatch_event(bot, "on_channel", sender_id, message, tags)