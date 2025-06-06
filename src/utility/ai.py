import json
import requests

from highrise import User
from config.config import config

def chat(prompt):
    url = config.url
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt
    }
    print(f"DEBUG: Sending to AI server: url={url}, data={data}")  # Debug print
    fallback_message_ai = config.messages['fallback_message_ai']
    try:
        chat_response = fallback_message_ai
        iterations = 0
        while True:
            iterations += 1
            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(f"DEBUG: AI server response: status={response.status_code}, body={response.text}")  # Debug print
            response.raise_for_status()

            if response.status_code != 200:
                break

            chat_response = response.json().get("response", "")
            if iterations >= 5:
                chat_response = fallback_message_ai
                break
            if len(chat_response) <= 255:
                break 
        chat_response = remove_chars_until_punctuation(chat_response)
        if not chat_response:
            chat_response = fallback_message_ai
        # Remove repeating spaces and newlines
        cleaned_response = ' '.join(chat_response.strip().split())
        return cleaned_response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return fallback_message_ai

async def ask_bot(bot, user: User, question: str):
    room_users = await bot.highrise.get_room_users()
    if user is None:
        response = chat(question)
    else:
        prompt = (
            f"I will give you array of current users in this room and their positions. "
            f"Use this knowledge when needed. Current users in this room are: {room_users.content}. "
            f"The person that just said something is: \"{user.username}\". "
            f"And they said: \"{question}\". You do not respond to them. "
            f"You use role-play to describe your thought process. What you can do is anything that you could do on your own: "
            f"do something that this room allows, play with your phone, play a game on your own and stuff like that. "
            f"The important part is that you do not respond to them directly!"
        )
        response = chat(prompt)
    await bot.highrise.chat("\n" + response)
    
def remove_chars_until_punctuation(s):
    end_sentence_punctuation = set('!".).;>?]`|}~*')
    # Count punctuation marks in the string
    punctuation_count = sum(1 for char in s if char in end_sentence_punctuation)
    
    # If there is only one punctuation mark, return the original string
    if punctuation_count <= 1:
        return s
    
    index = len(s) - 1
    # Iterate backward from the end of the string
    while index >= 0 and s[index] not in end_sentence_punctuation:
        index -= 1
    # Return the substring up to and including the first punctuation mark
    return s[:index + 1]

# Commit message:
# refactor(ai): rename ai_fallback to ai_nonsense for AI nonsense fallback responses
#
# CHANGELOG.md entry:
# - refactor(ai): Renamed ai_fallback to ai_nonsense in config and code for AI nonsense fallback responses.


