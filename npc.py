import json

# Load existing NPC definitions from disk
try:
    with open('npcs.json', 'r') as f:
        NPC_DEFS = json.load(f)
except FileNotFoundError:
    NPC_DEFS = {}


def save_npcs():
    """Persist NPC definitions to disk."""
    with open('npcs.json', 'w') as f:
        json.dump(NPC_DEFS, f, indent=2)
