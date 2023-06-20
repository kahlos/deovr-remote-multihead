# Generated 2023-06-20 by ChatGPT4

import tkinter as tk
from tkinter import messagebox
import time
import json
import socket
import threading

class DeoVRClient:
    def __init__(self, gui, host='127.0.0.1', port=23554):
        self.gui = gui
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.receiver = None
        self.pinger = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.connected = True
        self.receiver = threading.Thread(target=self._receive)
        self.receiver.start()
        self.pinger = threading.Thread(target=self._start_ping)
        self.pinger.start()

    def disconnect(self):
        self.connected = False
        self.sock.close()
        self.receiver.join()
        self.pinger.join()

    def send(self, data):
        msg = json.dumps(data).encode('utf-8')
        length = len(msg)
        self.sock.sendall(length.to_bytes(4, 'big') + msg)

    def _receive(self):
        while self.connected:
            length = int.from_bytes(self.sock.recv(4), 'big')
            if length:
                msg = json.loads(self.sock.recv(length).decode('utf-8'))
                self.gui.update(msg)

    def _start_ping(self):
        while self.connected:
            self.send({})
            time.sleep(1)


class DeoVRGui:
    def __init__(self):
        self.client = DeoVRClient(self)

        self.window = tk.Tk()
        self.window.title("DeoVR Remote Control test client v0.01")
        
        # Define all the GUI controls similar to the original C# application
        self.connect_button = tk.Button(self.window, text="Connect", command=self.connect_button_clicked)
        self.connect_button.pack()
        
        self.disconnect_button = tk.Button(self.window, text="Disconnect", command=self.disconnect_button_clicked)
        self.disconnect_button.pack()

        self.hostname_entry = tk.Entry(self.window)
        self.hostname_entry.pack()

        self.port_entry = tk.Entry(self.window)
        self.port_entry.pack()

        self.path_entry = tk.Entry(self.window)
        self.path_entry.pack()

        self.open_path_button = tk.Button(self.window, text="Open Path", command=self.open_path_button_clicked)
        self.open_path_button.pack()

        self.play_button = tk.Button(self.window, text="Play", command=self.play_button_clicked)
        self.play_button.pack()

        self.pause_button = tk.Button(self.window, text="Pause", command=self.pause_button_clicked)
        self.pause_button.pack()

    def connect_button_clicked(self):
        try:
            self.client.connect()
            messagebox.showinfo("Connection status", "Successfully connected")
        except Exception as e:
            messagebox.showerror("Connection status", f"Failed to connect: {e}")

    def disconnect_button_clicked(self):
        try:
            self.client.disconnect()
            messagebox.showinfo("Connection status", "Successfully disconnected")
        except Exception as e:
            messagebox.showerror("Connection status", f"Failed to disconnect: {e}")

    def open_path_button_clicked(self):
        path = self.path_entry.get()
        self.client.send({"path": path})

    def play_button_clicked(self):
        self.client.send({"playerState": 0})

    def pause_button_clicked(self):
        self.client.send({"playerState": 1})

    def update(self, data):
        # Here you should update the GUI with received data
        pass

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = DeoVRGui()
    gui.run()
