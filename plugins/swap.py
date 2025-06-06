from highrise import User, Position
from config.config import messages
import asyncio
from src.commands.command_base import CommandBase
from collections import deque
import time

# Global swap history buffer: key is tuple of user ids, value is deque of last 3 swaps
swap_history = {}

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):

        # # If no arguments are provided, show usage instructions
        if not args:
            await self.bot.highrise.chat("Usage: !swap @user1 [@user2]")
            return

        # # Helper to extract username from @mention
        def extract_username(arg):
            return arg.lstrip("@")

        # # Get mentioned usernames
        usernames = [extract_username(arg) for arg in args if arg.startswith("@")]
        if not usernames:
            await self.bot.highrise.chat("Please mention at least one user to swap with.")
            return

        await self.bot.highrise.chat(usernames)

        # # If only one user is mentioned, use the caller as user1
        if len(usernames) == 1:
            username1 = user.username
            username2 = usernames[0]
        else:
            username1, username2 = usernames[:2]

        await self.bot.highrise.chat(f"Swapping positions between {username1} and {username2}...")

        # # Get all users in the room
        room_users_resp = await self.bot.highrise.get_room_users()
        if hasattr(room_users_resp, 'content'):
            users_positions = room_users_resp.content
        else:
            await self.bot.highrise.chat("Failed to get room users.")
            return

        await self.bot.highrise.chat(str(users_positions))

        # # Find User and Position objects for both users
        user1 = user2 = pos1 = pos2 = None
        for u, pos in users_positions:
            if u.username.lower() == username1.lower():
                user1, pos1 = u, pos
            elif u.username.lower() == username2.lower():
                user2, pos2 = u, pos
        if not user1 or not user2 or not pos1 or not pos2:
            await self.bot.highrise.chat("Could not find both users in the room.")
            return

        await self.bot.highrise.chat(f"Found users: {user1.username} at {pos1}, {user2.username} at {pos2}")

        # # Identify caller and other user regardless of argument order
        caller_user_id = user.id
        if user1.id == caller_user_id:
            caller_user, caller_pos = user1, pos1
            other_user, other_pos = user2, pos2
        else:
            caller_user, caller_pos = user2, pos2
            other_user, other_pos = user1, pos1

        await self.bot.highrise.chat(f"Caller: {caller_user.username} at {caller_pos}, Other: {other_user.username} at {other_pos}")

        # # Only allow swapping if the caller is one of the users
        if caller_user.id != caller_user_id:
            await self.bot.highrise.chat("You can only swap your position with another user, not two other users.")
            return

        # # Both users must have Position (not AnchorPosition)
        if not (hasattr(caller_pos, 'x') and hasattr(caller_pos, 'y') and hasattr(caller_pos, 'z') and hasattr(other_pos, 'x') and hasattr(other_pos, 'y') and hasattr(other_pos, 'z')):
            await self.bot.highrise.chat("Both users must be on the floor to swap positions.")
            return

        temp_pos = Position(x=caller_pos.x, y=caller_pos.y, z=caller_pos.z)
        temp_pos2 = Position(x=other_pos.x, y=other_pos.y, z=other_pos.z)
        await self.bot.highrise.chat(f"Temporarily storing {caller_user.username}'s position at {temp_pos}...")
        await self.bot.highrise.chat(f"Swapping positions: {caller_user.username} at {caller_pos} with {other_user.username} at {other_pos}...")
        await self.bot.highrise.teleport(caller_user.id, Position(x=other_pos.x, y=other_pos.y, z=other_pos.z))
        await self.bot.highrise.teleport(other_user.id, Position(x=temp_pos.x, y=temp_pos.y, z=temp_pos.z))

        # Wait 2 seconds, then check if both users are back at their original positions
        await asyncio.sleep(2)
        room_users_resp2 = await self.bot.highrise.get_room_users()
        if hasattr(room_users_resp2, 'content'):
            users_positions2 = room_users_resp2.content
        else:
            await self.bot.highrise.chat("Failed to get room users after swap.")
            return

        # Find current positions of both users
        new_pos1 = new_pos2 = None
        for u, pos in users_positions2:
            if u.id == caller_user.id:
                new_pos1 = pos
            elif u.id == other_user.id:
                new_pos2 = pos

        # Compare with original positions
        same1 = (hasattr(new_pos1, 'x') and new_pos1.x == caller_pos.x and new_pos1.y == caller_pos.y and new_pos1.z == caller_pos.z)
        same2 = (hasattr(new_pos2, 'x') and new_pos2.x == other_pos.x and new_pos2.y == other_pos.y and new_pos2.z == other_pos.z)
        if same1 and same2:
            await self.bot.highrise.chat(f"{caller_user.username} at {new_pos1}, {other_user.username} at {new_pos2}")
            await self.bot.highrise.chat("same positions")
            # Teleport both users to their original positions using temp_pos and temp_pos2
            await self.bot.highrise.teleport(caller_user.id, temp_pos)
            await self.bot.highrise.teleport(other_user.id, temp_pos2)
            await self.bot.highrise.chat("same positions command")
