class Skill:
    """Represents a combat or support ability with cooldown."""

    def __init__(self, name, kind, power, stat=None, duration=0, cooldown=60):
        self.name = name
        self.kind = kind  # damage, heal, buff
        self.power = power
        self.stat = stat
        self.duration = duration
        self.cooldown = cooldown
        self.timer = 0

    def update(self):
        if self.timer > 0:
            self.timer -= 1

    def use(self, user, enemies):
        """Apply the skill's effect if off cooldown."""
        if self.timer > 0:
            return
        self.timer = self.cooldown
        if self.kind == 'damage':
            for enemy in enemies:
                if user.rect.colliderect(enemy.rect.inflate(20, 20)):
                    dmg = max(0, self.power - getattr(enemy, 'defense', 0))
                    enemy.take_damage(dmg)
                    break
        elif self.kind == 'heal':
            user.health = min(user.max_health, user.health + self.power)
        elif self.kind == 'buff' and self.stat:
            setattr(user, self.stat, getattr(user, self.stat) + self.power)
            user.active_buffs.append({'stat': self.stat, 'power': self.power, 'timer': self.duration})


SKILL_DEFS = {
    "Slash": {"kind": "damage", "power": 20, "cooldown": 30},
    "Shield Block": {"kind": "buff", "stat": "defense", "power": 5, "duration": 300, "cooldown": 300},
    "Arcane Strike": {"kind": "damage", "power": 25, "cooldown": 45},
    "Mana Shield": {"kind": "buff", "stat": "defense", "power": 8, "duration": 300, "cooldown": 300},
    "Arrow Shot": {"kind": "damage", "power": 15, "cooldown": 30},
    "Multi Shot": {"kind": "damage", "power": 10, "cooldown": 45},
    "Fireball": {"kind": "damage", "power": 30, "cooldown": 60},
    "Ice Bolt": {"kind": "damage", "power": 25, "cooldown": 60},
    "Inspiring Tune": {"kind": "buff", "stat": "attack", "power": 3, "duration": 300, "cooldown": 300},
    "Distracting Chord": {"kind": "damage", "power": 5, "cooldown": 30},
    "Heal": {"kind": "heal", "power": 25, "cooldown": 180},
    "Blessing": {"kind": "buff", "stat": "defense", "power": 5, "duration": 300, "cooldown": 300},
}


def create_skill(name):
    data = SKILL_DEFS.get(name)
    if not data:
        return None
    return Skill(name, **data)
