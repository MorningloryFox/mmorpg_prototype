# database.py
import json
import bcrypt
import os

DATABASE_FILE = 'database.json'

def load_data():
    if not os.path.exists(DATABASE_FILE):
        return {'users': {}}
    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user(username):
    data = load_data()
    return data['users'].get(username)

def create_user(username, password, char_class, is_admin=False):
    data = load_data()
    if username in data['users']:
        return False  # User already exists

    character = {
        'class': char_class,
        'level': 1,
        'xp': 0,
        'quests': {}
    }

    data['users'][username] = {
        'password': hash_password(password),
        'is_admin': is_admin,
        'characters': [character]
    }
    save_data(data)
    return True


def save_user_quests(username, quests):
    data = load_data()
    user = data['users'].get(username)
    if not user or not user['characters']:
        return
    user['characters'][0]['quests'] = quests
    save_data(data)

def setup_database():
    """Initializes the database with a default admin user."""
    print("Setting up the database...")
    if not get_user('admin'):
        create_user('admin', 'admin', 'Warrior', is_admin=True)
        print("Admin user 'admin' with password 'admin' created.")
    else:
        print("Admin user already exists.")
    print("Database setup complete.")

if __name__ == '__main__':
    # This allows running the script directly to set up the database
    setup_database()
