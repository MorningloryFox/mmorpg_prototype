import socket
import threading
import json

import database as db


class Server:
    """Simple TCP server for handling login and player position sync."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.clients = {}  # connection -> username
        self.positions = {}  # username -> {"x": int, "y": int}
        self.lock = threading.Lock()

    def start(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            conn, _ = sock.accept()
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn: socket.socket) -> None:
        username = None
        file = conn.makefile("r")
        for line in file:
            data = json.loads(line)
            action = data.get("action")
            if action == "login":
                username = self._handle_login(conn, data)
            elif action == "pos" and username:
                self._handle_position(username, data, exclude=conn)
        # client disconnected
        if username:
            with self.lock:
                self.clients.pop(conn, None)
                self.positions.pop(username, None)
            self.broadcast({"action": "leave", "username": username}, exclude=conn)
        conn.close()

    def _handle_login(self, conn: socket.socket, data: dict) -> str | None:
        username = data.get("username", "")
        password = data.get("password", "")
        user = db.get_user(username)
        if user and db.verify_password(user["password"], password):
            with self.lock:
                self.clients[conn] = username
                self.positions.setdefault(username, {"x": 0, "y": 0})
            response = {
                "action": "login",
                "status": "ok",
                "is_admin": user.get("is_admin", False),
                "players": self.positions,
            }
            conn.sendall(json.dumps(response).encode() + b"\n")
            # notify others about new player
            self.broadcast(
                {"action": "join", "username": username, "x": 0, "y": 0},
                exclude=conn,
            )
            return username
        conn.sendall(
            json.dumps({"action": "login", "status": "fail"}).encode() + b"\n"
        )
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

    def broadcast(self, message: dict, exclude: socket.socket | None = None) -> None:
        data = json.dumps(message).encode() + b"\n"
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
