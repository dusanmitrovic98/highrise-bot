import logging
import asyncio
from highrise import User
from config.config import config
from src.commands.command_base import CommandBase
from src.utility.ai import chat
from packages.radio_tts.main import say_on_radio

class Command(CommandBase):
    """
    Command to ask the AI a question and get a response.
    """
    def __init__(self, bot):
        super().__init__(bot)
        self.add_handler("on_chat", self.on_chat_handler)
        self.add_handler("on_message", self.on_message_handler)
        self.keywords = {"seb", "sebastian"}
        self._error_message = self.get_setting("error_message", "Sorry, something went wrong with the AI response.")
        self._thinking_message = self.get_setting("response_thinking_message", "\n 🤔")
        self.prefix = config.prefix

    @staticmethod
    def _extract_username(user_obj):
        """Extract username from user object, supporting nested user attribute."""
        return getattr(user_obj, "username", getattr(getattr(user_obj, "user", None), "username", None))

    def _should_respond(self, message: str):
        msg = message.strip().lower()
        if msg.startswith(f"{self.prefix}{self.name}"):
            return True
        return any(kw in msg.split() for kw in self.keywords)

    async def _get_users(self):
        users = await self.bot.highrise.get_room_users()
        return getattr(users, "content", users)

    @staticmethod
    def _extract_question(message: str, prefix: str = None, name: str = None) -> str:
        """Extract the question from the message, removing prefix and command name."""
        if prefix and name:
            return message.replace(f"{prefix}{name}", "").strip()
        return message.strip()

    async def _send_ai_response(self, question, username, users, send_func):
        """
        Send the AI response to the user. Handles both sync and async chat functions.
        """
        prompt = (
            f"[ASK] You can currently see these people {users}. "
            f"And you can there also see their IDs, usernames and coordinates in this room. "
            f"This prompt was asked by: {username}. {question}. "
            f"On this question you MUST DIRECTLY ANSWER!"
        )
        try:
            result = chat(prompt)
            if asyncio.iscoroutine(result):
                response = await result
            else:
                response = await asyncio.get_running_loop().run_in_executor(None, lambda: result)
            await send_func(response.strip())
            say_on_radio(response.strip())  # Stream the response on radio
        except Exception as e:
            await self._handle_error(send_func, f"[ASK] Error in ask response: {e}")

    @staticmethod
    async def _handle_error(send_func, log_message, error_message=None):
        msg = error_message or "Sorry, something went wrong with the AI response."
        await send_func(msg)
        logging.error(log_message, exc_info=True)

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command to get a response from the AI.
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        try:
            users = await self._get_users()
            question = self._extract_question(message, self.prefix, self.name)
            await self.bot.highrise.chat(self._thinking_message)
            username = self._extract_username(user)
            await self._send_ai_response(question, username, users, self.bot.highrise.chat)
        except Exception as e:
            await self._handle_error(self.bot.highrise.chat, f"[ASK] Error in ask command: {e}", self._error_message)

    def on_chat_handler(self, user: User, message: str):
        logging.debug(f"[ASK] on_chat_handler called with message: {message}")
        if not self._should_respond(message):
            return
        args = message.split()
        asyncio.create_task(self.execute(user, args, message))

    async def _send_dm(self, conversation_id, msg):
        await self.bot.highrise.send_message(conversation_id, msg)

    async def _handle_dm(self, user_id: str, conversation_id: str):
        """Async handler for DM events."""
        async def send_dm(msg):
            await self._send_dm(conversation_id, msg)
        try:
            user_info = await self.bot.webapi.get_user(user_id)
            messages_response = await self.bot.highrise.get_messages(conversation_id)
            messages = getattr(messages_response, "messages", [])
            if not messages:
                return
            last_msg = messages[0]
            message_content = getattr(last_msg, "content", "")
            if not self._should_respond(message_content):
                return
            users = await self._get_users()
            question = self._extract_question(message_content, self.prefix, self.name)
            username = self._extract_username(user_info)
            await self._send_ai_response(
                question, username, users, send_dm
            )
        except Exception as e:
            await self._handle_error(send_dm, f"[ASK] Error in on_message_handler: {e}", self._error_message)

    def on_message_handler(self, user_id: str, conversation_id: str, is_new_conversation: bool = False, *args, **kwargs):
        """
        Handler for DM events. Fetches the last message and triggers ask if prefix or keywords are found.
        Responds directly in DMs instead of public chat.
        """
        asyncio.create_task(self._handle_dm(user_id, conversation_id))