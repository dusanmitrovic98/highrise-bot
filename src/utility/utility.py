import json
import os

CONFIG_FOLDER = 'config'
PERMISSIONS_FILE = os.path.join(CONFIG_FOLDER, 'permissions.json')

def load_permissions():
    with open(PERMISSIONS_FILE, 'r') as file:
        return json.load(file)

def save_permissions(data):
    with open(PERMISSIONS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def user_exists(users, user_id):
    return any(user['user_id'] == user_id for user in users)

def username_exists(users, username):
    return any(user['username'] == username for user in users)

def get_user(users, user_id):
    for user in users:
        if user['user_id'] == user_id:
            return user
    return None

def get_user_id(users, username):
    for user in users:
        if user['username'] == username:
            return user['user_id']
    return None