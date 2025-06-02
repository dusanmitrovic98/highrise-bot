import logging


class config:
    # Basic configuration: If you are unsure how to obtain the Bot ID, simply start the bot and it will be logged in the console.
    url = "http://localhost:1234/v1"
    prefix = '/'
    botID = '66ab9e4865e341064df9df2b'
    botName = 'SebastianTheButler'
    ownerName = 'dule98'
    roomName = 'Night Club'
    coordinates = {
        'x': 5,
        'y': 0.6000,
        'z': 5,
        'facing': 'FrontRight'
    }
    modelAI = "gemma:2b"
    allowed_to_emote = False
    allowed_to_roam = False
    follow_user_id = None


class loggers:
    # The following settings are related to events. Each event log can be enabled or disabled. Note that turning these off will not affect their usage in the game.
    SessionMetadata = True
    messages = True
    whispers = True
    joins = True
    leave = True
    tips = True
    emotes = True
    reactions = True
    userMovement = True


class messages:
    # The following are optional and serve as a basic usage example for calling messages and replacing variables.
    invalidPosition = "Your position could not be determined."
    invalidPlayer = "{user} is not in the room."
    invalidUser = "User {user} is not found."
    invalidUsage = "Usage: {prefix}{commandName}{args}"
    invalidUserFormat = "Invalid user format. Please use '@username'."


class permissions:
    # You can add as many IDs as you want, for example: ['id1', 'id2'].
    owners = ['6807a86ebcff1952758703b3']
    moderators = ['6807a86ebcff1952758703b3']
    default = [
        "emote",
        "say",
        "ask"
    ]


class authorization:
    # To obtain your token, visit https://highrise.game/ and log in. Then, go to the settings and create a new bot. Accept the terms and generate a token.
    # To obtain your room ID, go to the game and navigate to the top right corner where the player list is displayed. Click on "Share this room" and copy the ID.
    room = '6807a86ebcff1952758703b3'
    token = '798993777281458fd5a108f82d6e421e15198a5500e1433e98b1f5b0262b98e4'


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
