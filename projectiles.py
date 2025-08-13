import json
from entities.projectile import Projectile

with open('projectiles.json', 'r') as f:
    PROJECTILE_DEFS = json.load(f)


def save_projectiles() -> None:
    with open('projectiles.json', 'w') as f:
        json.dump(PROJECTILE_DEFS, f, indent=2)


def create_projectile(pid: str, x: int, y: int, direction: str, walls, enemies, owner=None, base_damage: int = 0) -> Projectile:
    data = PROJECTILE_DEFS.get(pid, {})
    sprites = data.get('sprites') or ([data.get('sprite')] if data.get('sprite') else None)
    impact = data.get('impact')
    speed = data.get('speed', 10)
    damage = base_damage + data.get('damage', 0)
    return Projectile(x, y, direction, walls, enemies, damage, speed, owner, sprites=sprites, impact_sprite=impact)
