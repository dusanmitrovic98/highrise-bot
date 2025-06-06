from highrise.models import AnchorPosition, Position, User

from .dispatch_util import dispatch_event

async def on_move(bot, user: User, destination: Position | AnchorPosition) -> None:
    await dispatch_event(bot, "on_move", user, destination)