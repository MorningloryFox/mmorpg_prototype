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

def create_user(username, password, is_admin=False):
    data = load_data()
    if username in data['users']:
        return False # User already exists
    
    data['users'][username] = {
        'password': hash_password(password),
        'is_admin': is_admin,
        'characters': []
    }
    save_data(data)
    return True

def setup_database():
    """Initializes the database with a default admin user."""
    print("Setting up the database...")
    if not get_user('admin'):
        create_user('admin', 'admin', is_admin=True)
        print("Admin user 'admin' with password 'admin' created.")
    else:
        print("Admin user already exists.")
    print("Database setup complete.")

if __name__ == '__main__':
    # This allows running the script directly to set up the database
    setup_database()
