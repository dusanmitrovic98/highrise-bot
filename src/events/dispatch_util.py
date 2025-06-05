# Utility to dispatch event handlers for all commands/plugins
import inspect


async def dispatch_event(bot, event_name, *args):
    """
    Dispatches the event to all plugin/command handlers for the given event name.
    :param bot: The bot instance.
    :param event_name: The event name string (e.g., 'on_chat', 'on_join', etc.).
    :param args: Arguments to pass to the handler.
    """
    for command in getattr(bot, 'commands', []):
        for handler in getattr(command, 'get_handlers', lambda x: [])(event_name):
            if callable(handler):
                result = handler(*args)
                if inspect.isawaitable(result):
                    await result
            elif handler is not None:
                # Not callable, but not None: log or ignore
                pass
