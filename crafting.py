import json
from item import ITEM_DEFS


class Crafting:
    """Loadable recipe list and crafting helper."""

    def __init__(self, recipe_path: str = "crafting.json"):
        with open(recipe_path, "r") as f:
            self.recipes = json.load(f)

    def craft(self, player, recipe_id: str) -> bool:
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return False
        inputs = recipe.get("inputs", {})
        outputs = recipe.get("output", {})
        # verify player has required inputs
        for item_id, qty in inputs.items():
            if player.inventory.get(item_id, {"qty": 0})["qty"] < qty:
                return False
        # check inventory space for outputs
        needed_slots = 0
        for item_id in outputs:
            if item_id not in player.inventory:
                needed_slots += 1
        if len(player.inventory) + needed_slots > player.max_inventory_slots:
            return False
        # deduct inputs
        for item_id, qty in inputs.items():
            player.inventory[item_id]["qty"] -= qty
            if player.inventory[item_id]["qty"] <= 0:
                del player.inventory[item_id]
        # add outputs
        for item_id, qty in outputs.items():
            item_def = ITEM_DEFS.get(item_id)
            if not item_def:
                continue
            if item_id in player.inventory:
                player.inventory[item_id]["qty"] += qty
            else:
                player.inventory[item_id] = {"item": item_def, "qty": qty}
        return True
