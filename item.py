import json
from dataclasses import dataclass

@dataclass
class Item:
    id: str
    type: str
    attack: int = 0
    defense: int = 0
    icon: str = ""


def load_items(path: str = 'items.json'):
    with open(path, 'r') as f:
        data = json.load(f)
    items = {}
    for item_id, attrs in data.items():
        items[item_id] = Item(id=item_id, **attrs)
    return items

# cache loaded items
ITEM_DEFS = load_items()
