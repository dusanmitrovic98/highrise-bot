import json
import os
import subprocess

CONFIG_FOLDER = 'config'
PERMISSIONS_FILE = os.path.join(CONFIG_FOLDER, 'permissions.json')
PORTS_REGISTER_FILE = os.path.join('runtime', 'ports', 'register.json')

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

def kill_process_on_port(port):
    result = subprocess.run(
        f'netstat -ano | findstr :{port}',
        shell=True,
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().split('\n')
    for line in lines:
        if line:
            parts = line.split()
            pid = parts[-1]
            if pid != "0":
                os.system(f"taskkill /PID {pid} /F")

def load_registered_ports():
    if not os.path.exists(PORTS_REGISTER_FILE):
        return []
    with open(PORTS_REGISTER_FILE, 'r') as file:
        data = json.load(file)
        return data.get('ports', [])

def save_registered_ports(ports):
    with open(PORTS_REGISTER_FILE, 'w') as file:
        json.dump({'ports': ports}, file, indent=4)

def register_port(package_name, port):
    ports = load_registered_ports()
    # Remove any existing entry for this port or package
    ports = [p for p in ports if p['port'] != port and p['package'] != package_name]
    ports.append({'package': package_name, 'port': port})
    save_registered_ports(ports)

def unregister_port(package_name=None, port=None):
    ports = load_registered_ports()
    if package_name:
        ports = [p for p in ports if p['package'] != package_name]
    if port:
        ports = [p for p in ports if p['port'] != port]
    save_registered_ports(ports)

def kill_all_registered_ports():
    ports = load_registered_ports()
    for entry in ports:
        kill_process_on_port(entry['port'])