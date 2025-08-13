import threading
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class ServerPanel:
    """Tkinter-based admin panel for the Server."""

    def __init__(self, server):
        self.server = server
        self.root = tk.Tk()
        self.root.title("Server Panel")

        # player list
        cols = ("name", "id", "x", "y", "ip")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
        self.tree.pack(fill=tk.BOTH, expand=True)

        # log window
        self.log = tk.Text(self.root, height=10)
        self.log.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Global", command=self.global_message).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Teleport", command=self.teleport_player).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Kick", command=self.kick_player).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Ban", command=self.ban_player).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Mute", command=self.mute_player).pack(side=tk.LEFT)

        self.refresh()

    def refresh(self):
        # update players
        for item in self.tree.get_children():
            self.tree.delete(item)
        for name, pos in self.server.positions.items():
            pid = self.server.client_ids.get(name, 0)
            ip = self.server.client_ips.get(name, "")
            self.tree.insert("", tk.END, iid=name, values=(name, pid, pos["x"], pos["y"], ip))
        # update logs
        self.log.delete("1.0", tk.END)
        for line in self.server.logs[-200:]:
            self.log.insert(tk.END, line + "\n")
        self.root.after(1000, self.refresh)

    def _selected_player(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a player first")
            return None
        return sel[0]

    def global_message(self):
        text = simpledialog.askstring("Global Message", "Message:")
        if text:
            self.server.send_global(text)

    def teleport_player(self):
        player = self._selected_player()
        if not player:
            return
        x = simpledialog.askinteger("Teleport", "X:")
        y = simpledialog.askinteger("Teleport", "Y:")
        if x is not None and y is not None:
            self.server.teleport(player, x, y)

    def kick_player(self):
        player = self._selected_player()
        if player:
            self.server.kick(player)

    def ban_player(self):
        player = self._selected_player()
        if player:
            self.server.ban(player)

    def mute_player(self):
        player = self._selected_player()
        if player:
            self.server.mute(player)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    from network.server import Server

    srv = Server()
    threading.Thread(target=srv.start, daemon=True).start()
    panel = ServerPanel(srv)
    panel.run()
