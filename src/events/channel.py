from highrise.models import User
import logging

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

# TEMPORARY TEST: Simulate a channel event when this file is run directly
if __name__ == "__main__":
    import asyncio
    class DummyBot:
        class Highrise:
            async def send_whisper(self, user_id, msg):
                print(f"[WHISPER to {user_id}]: {msg}")
            async def chat(self, msg):
                print(f"[CHAT]: {msg}")
        highrise = Highrise()
    async def test():
        await on_channel(DummyBot(), "6807a86ebcff1952758703b3", "Test giveaway entry", {"giveaway"})
    asyncio.run(test())
