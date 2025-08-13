import json
from item import ITEM_DEFS

try:
    with open("shops.json", "r") as f:
        SHOPS = json.load(f)
except FileNotFoundError:
    SHOPS = {}


def save_shops() -> None:
    """Persist shop definitions to disk."""
    with open("shops.json", "w") as f:
        json.dump(SHOPS, f, indent=2)


class Shop:
    """Simple shop for buying and selling items using gold."""

    def __init__(self, shop_id: str = "general"):
        self.shop_id = shop_id
        self.stock = SHOPS.get(shop_id, [])

    def buy(self, player, item_id: str) -> bool:
        entry = next((e for e in self.stock if e.get("id") == item_id), None)
        if not entry:
            return False
        price = entry.get("buy", 0)
        if player.gold < price:
            return False
        item_def = ITEM_DEFS.get(item_id)
        if not item_def:
            return False
        player.gold -= price
        if item_id in player.inventory:
            player.inventory[item_id]["qty"] += 1
        else:
            if len(player.inventory) >= player.max_inventory_slots:
                return False
            player.inventory[item_id] = {"item": item_def, "qty": 1}
        return True

    def sell(self, player, item_id: str) -> bool:
        if item_id not in player.inventory:
            return False
        entry = next((e for e in self.stock if e.get("id") == item_id), None)
        price = 0
        if entry:
            price = entry.get("sell", entry.get("buy", 0) // 2)
        player.inventory[item_id]["qty"] -= 1
        if player.inventory[item_id]["qty"] <= 0:
            del player.inventory[item_id]
        player.gold += price
        return True
