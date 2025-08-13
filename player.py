# player.py
import pygame
import random
from settings import *
from item import ITEM_DEFS, Item
from skills import create_skill


class Party:
    """Simple party grouping players together."""

    def __init__(self, leader: "Player") -> None:
        self.leader = leader
        self.members = [leader]

    def add_member(self, player: "Player") -> None:
        if player not in self.members:
            self.members.append(player)
            player.party = self

    def remove_member(self, player: "Player") -> None:
        if player in self.members:
            self.members.remove(player)
            player.party = None
            if self.leader == player and self.members:
                self.leader = self.members[0]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Carregar sprites de animação (placeholders, can be replaced per class)
        self.idle_image = pygame.image.load("data/Bot/Bot Wheel/static idle.png").convert_alpha()
        self.walk_image_original = pygame.image.load("data/Bot/Bot Wheel/move with FX.png").convert_alpha()

        self.image = self.idle_image
        self.rect = self.image.get_rect(center=(x, y))

        self.speed = 5
        self.name = "Player"
        self.guild = None
        self.health = 100
        self.max_health = 100
        self.attack = 15
        self.defense = 5
        self.base_attack = self.attack
        self.base_defense = self.defense
        self.base_max_health = self.max_health
        self.level = 1
        self.xp = 0
        self.required_xp = 200
        self.inventory = {}
        self.max_inventory_slots = 10
        self.gold = 0
        self.character_class = None
        self.party = None
        self.quests = {}
        self.moving = False
        self.direction = "right"
        self.hit_timer = 0
        self.damage_cooldown = 0
        self.skills = []
        self.skill_defs = []
        self.active_buffs = []
        self.class_growth = {}
        self.attribute_points = 0
        # Attributes
        self.strength = 0
        self.constitution = 0
        self.intelligence = 0
        self.dexterity = 0
        self.luck = 0
        self.crit = 0
        self.equipment = {}
        try:
            self.attack_sound = pygame.mixer.Sound("sounds/attack.wav")
            self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        except pygame.error:
            self.attack_sound = None
            self.hit_sound = None

    def move(self, keys, walls, enemies):
        self.moving = False
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = "right"
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        if dx != 0 or dy != 0:
            self.moving = True

        # Move in x and check for collisions
        self.rect.x += dx
        for sprite in walls.sprites() + enemies.sprites():
            if self.rect.colliderect(sprite.rect):
                if dx > 0: # Moving right
                    self.rect.right = sprite.rect.left
                if dx < 0: # Moving left
                    self.rect.left = sprite.rect.right
        
        # Move in y and check for collisions
        self.rect.y += dy
        for sprite in walls.sprites() + enemies.sprites():
            if self.rect.colliderect(sprite.rect):
                if dy > 0: # Moving down
                    self.rect.bottom = sprite.rect.top
                if dy < 0: # Moving up
                    self.rect.top = sprite.rect.bottom

        # Reduce damage cooldown timer
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

    def update_animation(self):
        if not self.moving:
            self.image = self.idle_image
        else:
            walk_image = self.walk_image_original
            if self.direction == 'left':
                self.image = pygame.transform.flip(walk_image, True, False)
            else:
                self.image = walk_image

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
        font = pygame.font.Font(None, 20)
        name_text = font.render(f"{self.name}:{self.level}", True, WHITE)
        pos = self.rect.move(-camera.camera.x, -camera.camera.y)
        name_x = pos.x + self.rect.width // 2 - name_text.get_width() // 2
        name_y = pos.y - 15
        if self.guild:
            guild_text = font.render(self.guild, True, WHITE)
            screen.blit(guild_text, (pos.x + self.rect.width // 2 - guild_text.get_width() // 2, name_y - 15))
        screen.blit(name_text, (name_x, name_y))

    def collect_resources(self, resources):
        for resource in resources.copy():
            if self.rect.colliderect(resource.rect):
                resource.kill()  # Remove from all groups
                item_id = getattr(resource, 'item_id', 'alien_resource')
                item_def = ITEM_DEFS.get(item_id)
                if not item_def:
                    continue
                if item_id in self.inventory:
                    self.inventory[item_id]['qty'] += 1
                else:
                    if len(self.inventory) < self.max_inventory_slots:
                        self.inventory[item_id] = {'item': item_def, 'qty': 1}
                self.add_xp(5)

    # --- Party Management ---

    def create_party(self) -> Party:
        if not self.party:
            self.party = Party(self)
        return self.party

    def join_party(self, party: Party) -> None:
        if party:
            party.add_member(self)

    def leave_party(self) -> None:
        if self.party:
            self.party.remove_member(self)

    def melee_attack(self, enemies):
        """Perform a melee attack in front of the player."""
        if self.attack_sound:
            self.attack_sound.play()
        attack_rect = self.rect.copy()
        if self.direction == "left":
            attack_rect.x -= self.rect.width
        else:
            attack_rect.x += self.rect.width
        for enemy in enemies:
            if attack_rect.colliderect(enemy.rect):
                damage = max(0, self.attack - enemy.defense)
                if random.random() < self.crit / 100:
                    damage *= 2
                enemy.take_damage(damage, self)

    def take_damage(self, dmg):
        """Apply damage to the player with cooldown and hit effect."""
        if self.damage_cooldown > 0:
            return
        self.health -= dmg
        if self.hit_sound:
            self.hit_sound.play()
        self.hit_timer = 5
        self.damage_cooldown = 30
        if self.health <= 0:
            self.kill()

    def add_xp(self, amount: int):
        self.xp += amount
        while self.xp >= self.required_xp:
            self.xp -= self.required_xp
            self.level += 1
            self.required_xp = int(200 * (self.level ** 2))
            self.attribute_points += 3
            if self.level % 10 == 0:
                self.attribute_points += 5
            self.max_health = self.base_max_health + int(self.constitution) * 5
            self.health = self.max_health
            self.check_skill_unlocks()

    def update(self):
        self.update_animation()
        if self.hit_timer > 0:
            self.hit_timer -= 1
            self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        for skill in self.skills:
            skill.update()
        for buff in self.active_buffs[:]:
            buff['timer'] -= 1
            if buff['timer'] <= 0:
                setattr(self, buff['stat'], getattr(self, buff['stat']) - buff['power'])
                self.active_buffs.remove(buff)

    def load_skills(self, ability_defs):
        """Store skill definitions and instantiate unlocked ones."""
        self.skill_defs = ability_defs
        self.check_skill_unlocks()

    def check_skill_unlocks(self):
        names = {sk.name for sk in self.skills}
        for data in self.skill_defs:
            if self.level >= data.get('unlock', 1) and data['name'] not in names:
                sk = create_skill(data['name'])
                if sk:
                    self.skills.append(sk)

    def use_skill(self, index, enemies):
        if 0 <= index < len(self.skills):
            self.skills[index].use(self, enemies)

    def allocate_attribute(self, attr):
        if self.attribute_points <= 0:
            return
        mult = self.class_growth.get(attr, 0.5)
        value = getattr(self, attr) + mult
        if attr in ('luck', 'crit'):
            setattr(self, attr, min(value, 50))
        else:
            setattr(self, attr, value)
        if attr == 'strength':
            self.attack = self.base_attack + int(self.strength)
        elif attr == 'constitution':
            self.defense = self.base_defense + int(self.constitution)
            self.max_health = self.base_max_health + int(self.constitution) * 5
        self.attribute_points -= 1
