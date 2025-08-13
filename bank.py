from item import ITEM_DEFS


class Bank:
    """Stores player items and gold."""

    def __init__(self):
        self.items: dict[str, dict] = {}
        self.gold: int = 0

    def deposit_item(self, player, item_id: str, qty: int = 1) -> bool:
        if item_id not in player.inventory or player.inventory[item_id]["qty"] < qty:
            return False
        player.inventory[item_id]["qty"] -= qty
        if player.inventory[item_id]["qty"] <= 0:
            del player.inventory[item_id]
        self.items.setdefault(item_id, {"item": ITEM_DEFS.get(item_id), "qty": 0})
        self.items[item_id]["qty"] += qty
        return True

    def withdraw_item(self, player, item_id: str, qty: int = 1) -> bool:
        if item_id not in self.items or self.items[item_id]["qty"] < qty:
            return False
        self.items[item_id]["qty"] -= qty
        if self.items[item_id]["qty"] <= 0:
            del self.items[item_id]
        player.inventory.setdefault(item_id, {"item": ITEM_DEFS.get(item_id), "qty": 0})
        player.inventory[item_id]["qty"] += qty
        return True

    def deposit_gold(self, player, amount: int) -> bool:
        if player.gold < amount:
            return False
        player.gold -= amount
        self.gold += amount
        return True

    def withdraw_gold(self, player, amount: int) -> bool:
        if self.gold < amount:
            return False
        self.gold -= amount
        player.gold += amount
        return True
