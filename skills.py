import json


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
                    enemy.take_damage(dmg, user)
                    break
        elif self.kind == 'heal':
            user.health = min(user.max_health, user.health + self.power)
        elif self.kind == 'buff' and self.stat:
            setattr(user, self.stat, getattr(user, self.stat) + self.power)
            user.active_buffs.append({'stat': self.stat, 'power': self.power, 'timer': self.duration})


with open('skills.json', 'r') as f:
    SKILL_DEFS = json.load(f)


def save_skills():
    with open('skills.json', 'w') as f:
        json.dump(SKILL_DEFS, f, indent=2)


def create_skill(name):
    data = SKILL_DEFS.get(name)
    if not data:
        return None
    return Skill(name, **data)
