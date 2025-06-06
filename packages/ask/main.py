import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from groq import Groq

from config.config import Config as config


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GROQ_API_KEY in the .env file.")

app = Flask(__name__)
groq_client = Groq(api_key=api_key)

model = config.model_groq

messagesV1 = [config.get_system_prompt("v1")]

def create_chat_completion(messages):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=config.max_tokens if messages == messagesV1 else None
        )
        response = chat_completion.choices[0].message.content
        response = response[:255] if len(response) > 255 else response
        print(f"Generated tokens: {len(response.split())}")
        print(response)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/v1', methods=['POST'])
def chat_v1():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    messagesV1.append({"role": "user", "content": prompt})
    if len(messagesV1) > 6:
        messagesV1[:] = [messagesV1[0]] + messagesV1[-5:]
    print(f"Messages V1: {messagesV1}")
    return create_chat_completion(messagesV1)

if __name__ == '__main__':
    app.run(host='localhost', port=5001)
