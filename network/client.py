import socket
import threading
import queue
from typing import Dict, Tuple, List

from . import encode, decode


class NetworkClient:
    """Client helper to communicate with the game server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.incoming: "queue.Queue[dict]" = queue.Queue()
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self) -> None:
        file = self.sock.makefile("r")
        for line in file:
            try:
                data = decode(line)
            except Exception:
                continue
            self.incoming.put(data)

    def send(self, message: dict) -> None:
        self.sock.sendall(encode(message))

    def login(self, username: str, password: str) -> Tuple[bool, Dict[str, Dict[str, int]], bool]:
        """Attempts to authenticate the user.

        Returns (success, players, is_admin).
        """
        self.send({"action": "login", "username": username, "password": password})
        while True:
            msg = self.incoming.get()
            if msg.get("action") == "login":
                return msg.get("status") == "ok", msg.get("players", {}), msg.get("is_admin", False)
            # keep other messages queued for later processing
            self.incoming.put(msg)

    def update_position(self, x: int, y: int) -> None:
        self.send({"action": "pos", "x": x, "y": y})

    def send_chat(self, text: str) -> None:
        """Send a chat message to the server."""
        self.send({"action": "chat", "text": text})

    def send_trade(self, target: str, item_id: str, qty: int = 1) -> None:
        self.send({"action": "trade", "target": target, "item_id": item_id, "qty": qty})

    def send_attack(self, atk_type: str, direction: str, x: int | None = None, y: int | None = None, damage: int = 0) -> None:
        self.send({"action": "attack", "type": atk_type, "dir": direction, "x": x, "y": y, "damage": damage})

    def send_skill(self, skill_name: str) -> None:
        self.send({"action": "skill", "skill": skill_name})

    def send_quest_state(self, quests: Dict[str, bool]) -> None:
        self.send({"action": "quest", "quests": quests})

    def get_messages(self) -> List[dict]:
        messages = []
        while not self.incoming.empty():
            messages.append(self.incoming.get())
        return messages
