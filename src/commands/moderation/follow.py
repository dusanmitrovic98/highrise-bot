import math

from src.commands.command_base import CommandBase
from src.handlers.handleCommands import get_user_permissions
from highrise.models import User
from config.config import config

def calculate_follow_position(user_pos, bot_pos, distance):
    if not user_pos or not hasattr(user_pos, 'x') or not hasattr(user_pos, 'z'):
        return user_pos  # fallback: go directly to user
    if not bot_pos or not hasattr(bot_pos, 'x') or not hasattr(bot_pos, 'z'):
        return user_pos  # fallback: go directly to user
    dx = user_pos.x - bot_pos.x
    dz = user_pos.z - bot_pos.z
    dist = math.hypot(dx, dz)
    if dist == 0 or distance is None:
        return user_pos  # already at user or no distance set
    # Calculate new position at the specified distance behind the user (from bot's current position)
    scale = max(0, dist - distance) / dist
    new_x = bot_pos.x + dx * scale
    new_z = bot_pos.z + dz * scale
    # y and facing remain the same as user's
    return type(user_pos)(x=new_x, y=user_pos.y, z=new_z, facing=getattr(user_pos, 'facing', None))

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        user_permissions = get_user_permissions(user)
        # Only allow owners
        if not ("*" in user_permissions or "owner" in user_permissions):
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to use the follow command.")
            return
        # Parse arguments as key=value pairs, all optional (e.g., @username distance=1.0 timeout=30)
        target_user_id = user.id
        target_username = user.username
        distance = None
        timeout = None
        enabled = None
        # Parse @username if present as first arg
        arg_idx = 0
        if args and args[0].startswith("@"):  # Username mention
            username = args[0][1:]
            response = await self.bot.highrise.get_room_users()
            users = [content[0] for content in response.content]
            for u in users:
                if u.username.lower() == username.lower():
                    target_user_id = u.id
                    target_username = u.username
                    break
            else:
                await self.bot.highrise.send_whisper(user.id, f"User {username} not found in the room.")
                return
            arg_idx = 1  # Start parsing key=value from next arg
        # Parse key=value arguments and support 'infinite' for timeout
        for arg in args[arg_idx:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                key = key.strip().lower()
                value = value.strip()
                if key == 'distance':
                    try:
                        distance = float(value)
                    except Exception:
                        pass
                elif key == 'timeout':
                    if value.lower() == 'infinite':
                        timeout = 'infinite'
                    else:
                        try:
                            timeout = int(value)
                        except Exception:
                            pass
                elif key == 'enabled':
                    if value.lower() in ['yes', 'true', '1']:
                        enabled = True
                    elif value.lower() in ['no', 'false', '0']:
                        enabled = False
                    else:
                        enabled = None
                else:
                    enabled = None
            elif arg.lower() in ["enabled", "enable", "en"]:
                enabled = True
            elif arg.lower() in ["disabled", "disable", "dis"]:
                enabled = False
        # Get target user's coordinates and facing for follow logic
        coordinates = None
        facing = None
        response = await self.bot.highrise.get_room_users()
        users = [content[0] for content in response.content]
        for content in response.content:
            if content[0].id == target_user_id:
                pos_obj = content[1] if len(content) > 1 else None
                if pos_obj and hasattr(pos_obj, 'x') and hasattr(pos_obj, 'y') and hasattr(pos_obj, 'z'):
                    coordinates = {
                        "x": pos_obj.x,
                        "y": pos_obj.y,
                        "z": pos_obj.z,
                        "facing": getattr(pos_obj, "facing", None)
                    }
                    facing = getattr(pos_obj, "facing", None)
                break
        # Update follow_user action in config with all relevant parameters (including coordinates/facing as dicts)
        follow_action = config.actions["follow_user"]
        follow_action.id = target_user_id
        follow_action.name = target_username
        follow_action.coordinates = coordinates
        follow_action.facing = facing
        if distance is not None:
            follow_action.distance = distance
        if timeout is not None:
            follow_action.timeout = timeout
        if 'enabled' in locals() and enabled is not None:
            follow_action.enabled = enabled
        # Special case: allow 'enabled', 'enable', 'en', 'disable', 'disabled', 'dis' as single arg to toggle follow
        if len(args) == 1 and args[0].lower() in ["enabled", "enable", "en"]:
            follow_action.enabled = True
            # Persist config changes
            def configsection_to_dict(obj):
                if isinstance(obj, dict):
                    return {k: configsection_to_dict(v) for k, v in obj.items()}
                elif hasattr(obj, '__dict__'):
                    return {k: configsection_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__') and not callable(v)}
                else:
                    return obj
            from config.config import set_section
            set_section('actions', configsection_to_dict(config.actions))
            await self.bot.highrise.send_whisper(user.id, "Follow enabled. Bot will follow the configured user when they move.")
            return
        if len(args) == 1 and args[0].lower() in ["disabled", "disable", "dis"]:
            follow_action.enabled = False
            def configsection_to_dict(obj):
                if isinstance(obj, dict):
                    return {k: configsection_to_dict(v) for k, v in obj.items()}
                elif hasattr(obj, '__dict__'):
                    return {k: configsection_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__') and not callable(v)}
                else:
                    return obj
            from config.config import set_section
            set_section('actions', configsection_to_dict(config.actions))
            await self.bot.highrise.send_whisper(user.id, "Follow disabled. Bot will not follow anyone.")
            return
        # Persist config changes
        def configsection_to_dict(obj):
            if isinstance(obj, dict):
                return {k: configsection_to_dict(v) for k, v in obj.items()}
            elif hasattr(obj, '__dict__'):
                return {k: configsection_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__') and not callable(v)}
            else:
                return obj
        # Persist config changes
        from config.config import set_section
        set_section('actions', configsection_to_dict(config.actions))
        # Start timeout countdown if enabled and timeout is set (not 'infinite')
        follow_action = config.actions["follow_user"]
        # Only start a new timeout task if one isn't already running, and only if timeout is not 'infinite'
        if follow_action.enabled and isinstance(follow_action.timeout, (int, float)) and follow_action.timeout > 0:
            if not hasattr(self.bot, '_follow_timeout_task') or self.bot._follow_timeout_task is None or self.bot._follow_timeout_task.done():
                import asyncio
                async def timeout_task():
                    while follow_action.enabled and isinstance(follow_action.timeout, (int, float)) and follow_action.timeout > 0:
                        await asyncio.sleep(1)
                        # Re-fetch the latest value from config in case it was changed externally
                        from config.config import config as live_config, set_section
                        live_follow_action = live_config.actions["follow_user"]
                        if not (live_follow_action.enabled and isinstance(live_follow_action.timeout, (int, float)) and live_follow_action.timeout > 0):
                            break
                        live_follow_action.timeout -= 1
                        # Persist config changes
                        def configsection_to_dict(obj):
                            if isinstance(obj, dict):
                                return {k: configsection_to_dict(v) for k, v in obj.items()}
                            elif hasattr(obj, '__dict__'):
                                return {k: configsection_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__') and not callable(v)}
                            else:
                                return obj
                        set_section('actions', configsection_to_dict(live_config.actions))
                    # After loop, check if we need to stop following
                    if live_follow_action.enabled and live_follow_action.timeout == 0:
                        live_follow_action.enabled = False
                        set_section('actions', configsection_to_dict(live_config.actions))
                        await self.bot.highrise.send_whisper(live_follow_action.id, f"@{live_follow_action.name} I am tired..")
                self.bot._follow_timeout_task = asyncio.create_task(timeout_task())
        # If timeout is 0, bot will not follow and will say it is tired
        if (follow_action.timeout == 0 or (isinstance(follow_action.timeout, str) and follow_action.timeout.lower() == '0')):
            follow_action.enabled = False
            def configsection_to_dict(obj):
                if isinstance(obj, dict):
                    return {k: configsection_to_dict(v) for k, v in obj.items()}
                elif hasattr(obj, '__dict__'):
                    return {k: configsection_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__') and not callable(v)}
                else:
                    return obj
            from config.config import set_section
            set_section('actions', configsection_to_dict(config.actions))
            await self.bot.highrise.send_whisper(user.id, "I am tired.. (timeout=0). I am not following.. Please set a positive timeout to enable following.")
            return
        # Send feedback to the command issuer
        await self.bot.highrise.send_whisper(user.id, f"Following {target_username} (id: {target_user_id}). Bot will move to their coordinates when they move. [distance={follow_action.distance}, timeout={follow_action.timeout}, enabled={follow_action.enabled}]")
