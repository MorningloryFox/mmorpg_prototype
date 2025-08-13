import pygame
from .common import Button, InputBox, Label
from shop import SHOPS, save_shops
from settings import WHITE


class ShopEditor:
    """Admin tool to configure shop inventories and prices."""

    def __init__(self):
        self.active = False
        panel_img = pygame.image.load(
            "data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png"
        ).convert_alpha()
        self.panel = pygame.transform.scale(panel_img, (400, 560))
        self.font = pygame.font.Font(None, 24)
        # Input fields
        self.shop_id = InputBox(260, 80, 120, 25)
        self.item_id = InputBox(260, 260, 120, 25)
        self.buy_price = InputBox(260, 300, 120, 25)
        self.sell_price = InputBox(260, 340, 120, 25)
        self.index_box = InputBox(260, 380, 120, 25)
        self.labels = [
            Label(160, 90, "Shop ID", font_size=20),
            Label(160, 270, "Item ID", font_size=20),
            Label(160, 310, "Buy", font_size=20),
            Label(160, 350, "Sell", font_size=20),
            Label(160, 390, "Index", font_size=20),
        ]
        # Buttons
        self.add_button = Button(260, 420, 120, 30, "Add", self.add_item)
        self.remove_button = Button(260, 460, 120, 30, "Remove", self.remove_item)
        self.up_button = Button(260, 500, 60, 30, "Up", self.move_up)
        self.down_button = Button(320, 500, 60, 30, "Down", self.move_down)
        self.save_button = Button(260, 540, 120, 30, "Save", save_shops)

    def toggle(self):
        self.active = not self.active

    def current_stock(self):
        shop_id = self.shop_id.text.strip()
        return SHOPS.setdefault(shop_id, []) if shop_id else []

    def add_item(self):
        shop_id = self.shop_id.text.strip()
        item_id = self.item_id.text.strip()
        if not shop_id or not item_id:
            return
        try:
            buy = int(self.buy_price.text or 0)
            sell = int(self.sell_price.text or 0)
        except ValueError:
            return
        stock = SHOPS.setdefault(shop_id, [])
        stock.append({"id": item_id, "buy": buy, "sell": sell})
        save_shops()
        self.item_id.text = ""
        self.buy_price.text = ""
        self.sell_price.text = ""

    def remove_item(self):
        shop_id = self.shop_id.text.strip()
        if not shop_id or not self.index_box.text.isdigit():
            return
        stock = SHOPS.get(shop_id)
        if not stock:
            return
        idx = int(self.index_box.text)
        if 0 <= idx < len(stock):
            stock.pop(idx)
            save_shops()
        self.index_box.text = ""

    def move_up(self):
        shop_id = self.shop_id.text.strip()
        if not shop_id or not self.index_box.text.isdigit():
            return
        stock = SHOPS.get(shop_id)
        if not stock:
            return
        idx = int(self.index_box.text)
        if 0 < idx < len(stock):
            stock[idx - 1], stock[idx] = stock[idx], stock[idx - 1]
            self.index_box.text = str(idx - 1)
            save_shops()

    def move_down(self):
        shop_id = self.shop_id.text.strip()
        if not shop_id or not self.index_box.text.isdigit():
            return
        stock = SHOPS.get(shop_id)
        if not stock:
            return
        idx = int(self.index_box.text)
        if 0 <= idx < len(stock) - 1:
            stock[idx + 1], stock[idx] = stock[idx], stock[idx + 1]
            self.index_box.text = str(idx + 1)
            save_shops()

    def handle_event(self, event):
        if not self.active:
            return
        for box in [
            self.shop_id,
            self.item_id,
            self.buy_price,
            self.sell_price,
            self.index_box,
        ]:
            box.handle_event(event)
        for btn in [
            self.add_button,
            self.remove_button,
            self.up_button,
            self.down_button,
            self.save_button,
        ]:
            btn.handle_event(event)

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (200, 60))
        stock = self.current_stock()
        y = 120
        for i, entry in enumerate(stock):
            text = self.font.render(
                f"{i}. {entry['id']} B:{entry.get('buy',0)} S:{entry.get('sell',0)}",
                True,
                WHITE,
            )
            screen.blit(text, (220, y))
            y += 20
        for label in self.labels:
            label.draw(screen)
        for box in [
            self.shop_id,
            self.item_id,
            self.buy_price,
            self.sell_price,
            self.index_box,
        ]:
            box.draw(screen)
        for btn in [
            self.add_button,
            self.remove_button,
            self.up_button,
            self.down_button,
            self.save_button,
        ]:
            btn.draw(screen)
