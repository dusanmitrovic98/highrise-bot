from highrise.models import User, Position, AnchorPosition
from config.config import loggers, config
import logging
import asyncio

timeout_task_running = False


async def on_move(bot, user: User, destination: Position | AnchorPosition) -> None:
    if loggers.userMovement:
        logging.info(f"{user.username} moved to {destination}")
    # Follow logic: if the bot is set to follow this user, move the bot to the same destination
    follow_action = getattr(config.actions, "follow_user", None)
    if follow_action and getattr(follow_action, "enabled", False) and getattr(follow_action, "id", None) == user.id:
        distance = getattr(follow_action, "distance", None)
        # Get bot's current position
        bot_user = None
        response = await bot.highrise.get_room_users()
        for content in response.content:
            if content[0].id == bot.highrise.my_id:
                bot_user = content[1] if len(content) > 1 else None
                break
        from src.commands.moderation.follow import calculate_follow_position
        dest = destination
        if distance is not None and bot_user is not None:
            dest = calculate_follow_position(destination, bot_user, distance)
        # Update coordinates and facing in config.actions['follow_user']
        from config.config import set_section
        def configsection_to_dict(obj):
            if isinstance(obj, dict):
                return {k: configsection_to_dict(v) for k, v in obj.items()}
            elif hasattr(obj, '__dict__'):
                return {k: configsection_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__') and not callable(v)}
            else:
                return obj
        follow_action.coordinates = {
            "x": dest.x,
            "y": dest.y,
            "z": dest.z,
            "facing": getattr(dest, "facing", None)
        }
        follow_action.facing = getattr(dest, "facing", None)
        set_section('actions', configsection_to_dict(config.actions))
        # Start timeout countdown if not already running and timeout is not 'infinite'
        global timeout_task_running
        if not timeout_task_running and isinstance(follow_action.timeout, (int, float)) and follow_action.timeout > 0:
            timeout_task_running = True
            async def timeout_task():
                from config.config import config as live_config, set_section
                def configsection_to_dict(obj):
                    if isinstance(obj, dict):
                        return {k: configsection_to_dict(v) for k, v in obj.items()}
                    elif hasattr(obj, '__dict__'):
                        return {k: configsection_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__') and not callable(v)}
                    else:
                        return obj
                while True:
                    await asyncio.sleep(1)
                    live_follow_action = live_config.actions["follow_user"]
                    if not (live_follow_action.enabled and isinstance(live_follow_action.timeout, (int, float)) and live_follow_action.timeout > 0):
                        break
                    live_follow_action.timeout -= 1
                    set_section('actions', configsection_to_dict(live_config.actions))
                if live_follow_action.enabled and live_follow_action.timeout == 0:
                    live_follow_action.enabled = False
                    set_section('actions', configsection_to_dict(live_config.actions))
                    await bot.highrise.send_whisper(live_follow_action.id, f"@{live_follow_action.name} I am tired..")
                global timeout_task_running
                timeout_task_running = False
            asyncio.create_task(timeout_task())
        await bot.highrise.walk_to(destination)
