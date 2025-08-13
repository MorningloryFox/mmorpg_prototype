import json

# Load dialogue definitions
try:
    with open('dialogues.json', 'r') as f:
        DIALOGUES = json.load(f)
except FileNotFoundError:
    DIALOGUES = {}


def save_dialogues():
    """Persist dialogue definitions to disk."""
    with open('dialogues.json', 'w') as f:
        json.dump(DIALOGUES, f, indent=2)
