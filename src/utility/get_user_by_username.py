# Utility to get user by username from room
async def get_user_by_username(bot, username):
    response = await bot.highrise.get_room_users()
    for u, pos in response.content:
        if u.username.lower() == username.lower():
            return u
    return None
