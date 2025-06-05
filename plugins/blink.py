import math
from highrise import User, Position
from config.config import messages
from src.commands.command_base import CommandBase

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        response = await self.bot.highrise.get_room_users()
        # Map usernames to (User, Position)
        user_map = {content[0].username.lower(): (content[0], content[1]) for content in response.content}
        usernames = list(user_map.keys())
        # Default values
        target_user = user
        blink_distance = 1.0
        target_username = user.username.lower()

        # Parse arguments
        direction = None
        if args:
            # Add short versions for directions
            directions = {
                "up", "down", "left", "right", "forward", "backward", "back",
                "u", "d", "l", "r", "f", "b"
            }
            # Map short to long
            dir_aliases = {
                "u": "up",
                "d": "down",
                "l": "left",
                "r": "right",
                "f": "forward",
                "b": "backward"
            }
            found_dirs = []
            for a in args:
                al = a.lower()
                if al in directions:
                    found_dirs.append(dir_aliases.get(al, al))
            if found_dirs:
                direction = found_dirs
                # Remove direction args for further parsing
                args = [a for a in args if a.lower() not in directions]

            if args:
                if args[0].startswith("@"):  # Targeting another user
                    username = args[0][1:].lower()
                    if username not in usernames:
                        await self.bot.highrise.send_whisper(user.id, f"{messages.invalidPlayer.format(user=args[0][1:])}")
                        return
                    target_user = user_map[username][0]
                    target_username = username
                    if len(args) > 1:
                        try:
                            blink_distance = float(args[1])
                        except ValueError:
                            await self.bot.highrise.send_whisper(user.id, "Invalid blink distance.")
                            return
                else:
                    try:
                        blink_distance = float(args[0])
                    except ValueError:
                        await self.bot.highrise.send_whisper(user.id, "Invalid blink distance.")
                        return

        # Get current position and facing direction
        pos = user_map[target_username][1]
        facing = getattr(pos, 'facing', 'FrontRight')
        # Facing is a string, map to angle in degrees (swap FrontLeft and BackLeft)
        facing_map = {
            'FrontRight': 90,
            'BackRight': 0,
            'BackLeft': 270,    # swapped with FrontLeft
            'FrontLeft': 180    # swapped with BackLeft
        }
        angle_deg = facing_map.get(facing, 90)

        # Direction vector logic (fix: combine, scale each direction independently, no normalization)
        dx, dy, dz = 0.0, 0.0, 0.0
        if direction:
            for dir in direction:
                if dir == "up":
                    dy += blink_distance
                elif dir == "down":
                    dy -= blink_distance
                elif dir == "left":
                    left_angle = angle_deg - 90
                    rad = math.radians(left_angle)
                    dx += math.cos(rad) * blink_distance
                    dz += math.sin(rad) * blink_distance
                elif dir == "right":
                    right_angle = angle_deg + 90
                    rad = math.radians(right_angle)
                    dx += math.cos(rad) * blink_distance
                    dz += math.sin(rad) * blink_distance
                elif dir in ("back", "backward"):
                    back_angle = angle_deg + 180
                    rad = math.radians(back_angle)
                    dx += math.cos(rad) * blink_distance
                    dz += math.sin(rad) * blink_distance
                elif dir == "forward":
                    rad = math.radians(angle_deg)
                    dx += math.cos(rad) * blink_distance
                    dz += math.sin(rad) * blink_distance
        else:
            # Default: forward
            rad = math.radians(angle_deg)
            dx = math.cos(rad) * blink_distance
            dz = math.sin(rad) * blink_distance

        new_x = pos.x + dx
        new_y = pos.y + dy
        new_z = pos.z + dz
        dest = Position(new_x, new_y, new_z, facing=facing)

        await self.bot.highrise.teleport(target_user.id, dest)
        await self.bot.highrise.send_whisper(user.id, f"Blinked {target_user.username} {blink_distance} unit(s) {' and '.join(direction) if direction else 'forward'}.")
