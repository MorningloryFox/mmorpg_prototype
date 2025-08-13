import json
from item import ITEM_DEFS, Item


class Shop:
    """Simple shop for buying and selling items using gold."""

    def __init__(self, stock_path: str | None = None):
        if stock_path:
            with open(stock_path, "r") as f:
                self.stock = json.load(f)
        else:
            self.stock = {"sword": {"price": 50}, "potion": {"price": 10}}

    def buy(self, player, item_id: str) -> bool:
        data = self.stock.get(item_id)
        if not data:
            return False
        price = data.get("price", 0)
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
        price = self.stock.get(item_id, {}).get("price", 0) // 2
        player.inventory[item_id]["qty"] -= 1
        if player.inventory[item_id]["qty"] <= 0:
            del player.inventory[item_id]
        player.gold += price
        return True
