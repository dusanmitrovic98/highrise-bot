from highrise import User
import requests
import os
import json

from config.config import config

# def chat(prompt):
#     llama_70B = "llama-3.1-70b-versatile"
#     url = "https://api.groq.com/openai/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "messages": [{"role": "user", "content": prompt}],
#         "model": llama_70B,
#         "max_tokens": 20
#     }
    
#     response = requests.post(url, headers=headers, json=data)
    
#     if response.status_code == 200:
#         return response.json().get('choices')[0].get('message').get('content')
#     else:
#         return f"Error: {response.status_code}, {response.text}"

def chat(prompt):
    url = config.url
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt
    }
    
    try:
        chat_response = "Sorry, can you ask me again later? I am kinda busy!"
        iterations = 0
        while True:
            iterations += 1
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()

            if response.status_code != 200:
                break

            chat_response = response.json().get("response", "")
            
            if iterations >= 5:
                chat_response = "Sorry, can you ask me again later? I am kinda SUPER busy!"
                break
            if len(chat_response) <= 255:
                break 
        
        chat_response = remove_chars_until_punctuation(chat_response)

        if not chat_response:
            chat_response = "Sorry, can you ask me again later? I am kinda SUPER busy!"
        return chat_response.strip()
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Sorry, there was a problem with the AI service."

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
# fix(ai): correct punctuation set syntax in remove_chars_until_punctuation
#
# CHANGELOG.md entry:
# - fix(ai): Fixed punctuation set syntax in remove_chars_until_punctuation to prevent syntax errors and improve response trimming.


