import json
from dataclasses import dataclass, asdict


@dataclass
class Item:
    id: str
    name: str
    description: str
    type: str
    icon: str = ""
    attack: int = 0
    defense: int = 0
    strength: int = 0
    agility: int = 0
    hp: int = 0


def load_items(path: str = "items.json"):
    with open(path, "r") as f:
        data = json.load(f)
    items = {}
    for item_id, attrs in data.items():
        items[item_id] = Item(id=item_id, **attrs)
    return items


def save_items(path: str = "items.json"):
    data = {}
    for item_id, item in ITEM_DEFS.items():
        item_dict = asdict(item)
        item_dict.pop("id", None)
        data[item_id] = item_dict
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# cache loaded items
ITEM_DEFS = load_items()
