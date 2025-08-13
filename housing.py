import json
from typing import Dict, List

HOUSING_FILE = 'housing.json'

def load_houses() -> List[Dict]:
    """Load housing claims from disk."""
    try:
        with open(HOUSING_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_houses(houses: List[Dict]) -> None:
    with open(HOUSING_FILE, 'w') as f:
        json.dump(houses, f)

def areas_overlap(a: Dict, b: Dict) -> bool:
    return not (a['x'] + a['w'] <= b['x'] or a['x'] >= b['x'] + b['w'] or
a['y'] + a['h'] <= b['y'] or a['y'] >= b['y'] + b['h'])

def claim_area(owner: str, rect: Dict) -> bool:
    """Claim an area for a player if it's free.``rect`` is dict with x,y,w,h."""
    houses = load_houses()
    for h in houses:
        if areas_overlap(h['rect'], rect):
            return False
    houses.append({'owner': owner, 'rect': rect})
    save_houses(houses)
    return True

def get_owner_at(x: int, y: int) -> str:
    """Return owner name if (x,y) lies within a claimed house."""
    houses = load_houses()
    for h in houses:
        r = h['rect']
        if r['x'] <= x < r['x'] + r['w'] and r['y'] <= y < r['y'] + r['h']:
            return h['owner']
    return ''
