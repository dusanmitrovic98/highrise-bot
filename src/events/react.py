from highrise.models import Reaction, User

from .dispatch_util import dispatch_event


async def on_reaction(bot, user: User, reaction: Reaction, receiver: User) -> None:
    await dispatch_event(bot, "on_reaction", user, reaction, receiver)
