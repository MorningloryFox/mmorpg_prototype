import socket
import threading

import database as db
import skills
import json
from . import encode, decode


class Server:
    """Simple TCP server for handling login and player position sync."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.clients = {}  # connection -> username
        self.positions = {}  # username -> {"x": int, "y": int}
        self.classes = {}  # username -> class name
        self.quests = {}  # username -> quest state
        self.admins = set()
        # extra state for admin panel
        self.client_ips: dict[str, str] = {}
        self.client_ids: dict[str, int] = {}
        self.next_id = 1
        self.banned = set()
        self.muted = set()
        self.logs: list[str] = []
        self.lock = threading.Lock()

    def start(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            conn, addr = sock.accept()
            threading.Thread(
                target=self.handle_client, args=(conn, addr), daemon=True
            ).start()

    def handle_client(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        username = None
        file = conn.makefile("r")
        for line in file:
            data = decode(line)
            action = data.get("action")
            if action == "login":
                username = self._handle_login(conn, addr, data)
            elif action == "pos" and username:
                self._handle_position(username, data, exclude=conn)
            elif action == "chat" and username:
                if username not in self.muted:
                    self.broadcast(
                        {
                            "action": "chat",
                            "username": username,
                            "text": data.get("text", ""),
                        }
                    )
            elif action == "trade" and username:
                self._handle_trade(username, data)
            elif action == "attack" and username:
                self._handle_attack(username, data)
            elif action == "skill" and username:
                self._handle_skill(username, data)
            elif action == "quest" and username:
                self._handle_quest(username, data)
            elif action == "admin" and username:
                self._handle_admin(username, data)
        # client disconnected
        if username:
            with self.lock:
                self.clients.pop(conn, None)
                self.positions.pop(username, None)
                self.client_ips.pop(username, None)
                self.client_ids.pop(username, None)
                self.admins.discard(username)
            self.broadcast({"action": "leave", "username": username}, exclude=conn)
        conn.close()

    def _handle_login(
        self, conn: socket.socket, addr: tuple[str, int], data: dict
    ) -> str | None:
        username = data.get("username", "")
        password = data.get("password", "")
        if username in self.banned:
            conn.sendall(encode({"action": "login", "status": "banned"}))
            return None
        user = db.get_user(username)
        if user and db.verify_password(user["password"], password):
            with self.lock:
                self.clients[conn] = username
                self.positions.setdefault(username, {"x": 0, "y": 0})
                self.client_ips[username] = addr[0]
                self.client_ids[username] = self.next_id
                self.next_id += 1
                char = user["characters"][0]
                self.classes[username] = char.get("class", "")
                self.quests[username] = char.get("quests", {})
                if user.get("is_admin", False):
                    self.admins.add(username)
            response = {
                "action": "login",
                "status": "ok",
                "is_admin": user.get("is_admin", False),
                "players": self.positions,
            }
            conn.sendall(encode(response))
            self.broadcast(
                {"action": "join", "username": username, "x": 0, "y": 0},
                exclude=conn,
            )
            self.log(f"{username} connected from {addr[0]}")
            return username
        conn.sendall(encode({"action": "login", "status": "fail"}))
        return None

    def _handle_position(self, username: str, data: dict, exclude: socket.socket) -> None:
        x = data.get("x", 0)
        y = data.get("y", 0)
        with self.lock:
            self.positions[username] = {"x": x, "y": y}
        self.broadcast(
            {"action": "pos", "username": username, "x": x, "y": y},
            exclude=exclude,
        )

    def _handle_trade(self, username: str, data: dict) -> None:
        message = {
            "action": "trade",
            "from": username,
            "to": data.get("target"),
            "item_id": data.get("item_id"),
            "qty": data.get("qty", 1),
        }
        self.broadcast(message)

    def _handle_attack(self, username: str, data: dict) -> None:
        atk_type = data.get("type")
        if atk_type not in {"melee", "projectile"}:
            return
        dmg = int(data.get("damage", 0))
        msg = {
            "action": "attack",
            "username": username,
            "type": atk_type,
            "dir": data.get("dir"),
            "x": data.get("x"),
            "y": data.get("y"),
            "damage": dmg,
        }
        self.broadcast(msg, exclude=None)

    def _handle_skill(self, username: str, data: dict) -> None:
        skill_name = data.get("skill")
        if skill_name not in skills.SKILL_DEFS:
            return
        msg = {"action": "skill", "username": username, "skill": skill_name}
        self.broadcast(msg, exclude=None)

    def _handle_quest(self, username: str, data: dict) -> None:
        quests = data.get("quests")
        if not isinstance(quests, dict):
            return
        with self.lock:
            self.quests[username] = quests
        self.broadcast({"action": "quest", "username": username, "quests": quests})

    def _handle_admin(self, username: str, data: dict) -> None:
        if username not in self.admins:
            return
        cmd = data.get("command")
        if not cmd:
            return
        log_entry = {
            "username": username,
            "command": cmd,
        }
        extra = {k: v for k, v in data.items() if k not in {"action", "command"}}
        if extra:
            log_entry.update(extra)
        with open("admin.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        self.broadcast({"action": "admin", **log_entry})

    # ---- admin panel helpers ----

    def send_global(self, text: str) -> None:
        self.broadcast({"action": "chat", "username": "[SERVER]", "text": text})
        self.log(f"GLOBAL: {text}")

    def kick(self, username: str) -> None:
        with self.lock:
            conn = next((c for c, u in self.clients.items() if u == username), None)
        if conn:
            try:
                conn.close()
            except OSError:
                pass
            self.log(f"Kicked {username}")

    def ban(self, username: str) -> None:
        self.banned.add(username)
        self.kick(username)
        self.log(f"Banned {username}")

    def mute(self, username: str) -> None:
        self.muted.add(username)
        self.log(f"Muted {username}")

    def teleport(self, username: str, x: int, y: int) -> None:
        self.broadcast({"action": "teleport", "username": username, "x": x, "y": y})
        self.log(f"Teleported {username} to {x},{y}")

    def log(self, message: str) -> None:
        with self.lock:
            self.logs.append(message)
        print(message)

    def broadcast(self, message: dict, exclude: socket.socket | None = None) -> None:
        data = encode(message)
        with self.lock:
            for conn in list(self.clients.keys()):
                if conn is exclude:
                    continue
                try:
                    conn.sendall(data)
                except OSError:
                    pass


if __name__ == "__main__":
    Server().start()
