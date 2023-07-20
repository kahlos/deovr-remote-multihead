# Generated by ChatGPT4 2023-06-20

# Import necessary libraries
import tkinter as tk  # used for creating the graphical user interface (GUI)
from tkinter import messagebox  # used for displaying messages to the user
import time  # used for controlling the timing of the program
import json  # used for encoding and decoding JSON data
import socket  # used for creating a network connection
import threading  # used for running multiple tasks at the same time
import atexit

class DeoVRClient:
    def __init__(self, gui, id, host='10.0.0.60', port=23554):
        # The constructor takes a gui object, a host address and a port number.
        # The gui object will be used to interact with the GUI.
        # The host and port will be used to connect to the DeoVR app.

        self.gui = gui
        self.id = id
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.receiver = None
        self.pinger = None

    def connect(self, hostname, port):
        # This method is called to connect to the DeoVR app.
        # A socket is created and connected to the specified host and port.
        # Two threads are started: one for receiving data from the app and one for pinging the app.
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Attempting to connect to {hostname}:{port}")  # debug log
            self.sock.connect((hostname, port))
            print("Connected successfully")  # debug log
            self.connected = True
            self.send({})
            self.receiver = threading.Thread(target=self._receive)
            self.receiver.start()
            self.pinger = threading.Thread(target=self._start_ping)
            self.pinger.start()
        except Exception as e:
            print(f"Failed to connect due to: {e}")  # debug log
            self.connected = False

    def disconnect(self):
        # This method is called to disconnect from the DeoVR app.
        # The socket is closed and the receiver and pinger threads are stopped.

        self.connected = False
        if self.sock is not None:  # add this line
            self.sock.close()
        if self.receiver is not None:  # check if receiver thread exists before joining
            self.receiver.join()
        if self.pinger is not None:  # check if pinger thread exists before joining
            self.pinger.join()

    def stop(self):
        self.connected = False
        if self.sock is not None:
            self.sock.close()
        if self.receiver is not None and self.receiver.is_alive():
            self.receiver.join()
        if self.pinger is not None and self.pinger.is_alive():
            self.pinger.join()


    def send(self, data):
        # This method is called to send data to the DeoVR app.
        # The data is encoded as JSON and then sent over the socket.

        if data:
            msg = json.dumps(data).encode('utf-8')
            length = len(msg)
            try:
                if self.sock:
                    self.sock.sendall(length.to_bytes(4, 'little') + msg)
            except Exception as e:
                print(f"Exception while sending data: {e}")
                # If an error occurs, close the socket and reopen the connection
                self.disconnect()
                time.sleep(1)
                self.connect()
        else:  # Sending a ping
            self.sock.sendall((0).to_bytes(4, 'little'))

    def _receive(self):
        # This method is run in a separate thread and is responsible for receiving data from the DeoVR app.
        # When data is received, it is decoded and passed to the GUI to update the interface.

        while self.connected:
            try:
                length = int.from_bytes(self.sock.recv(4), 'big')
                if length:
                    msg = json.loads(self.sock.recv(length).decode('utf-8'))
                    self.gui.update(msg)
            except Exception as e:
                print(f"Exception in receive: {e}")
                break  # Break the loop and end the thread if an exception occurs


    def _start_ping(self):
        # This method is run in a separate thread and is responsible for pinging the DeoVR app every second.
        # This keeps the connection to the app alive.

        while self.connected:
            try:
                self.send(None)  # Sending a ping
                time.sleep(1)
            except Exception as e:
                print(f"Exception in ping: {e}")
                break


class DeoVRGui:
    def __init__(self):
        # Constructor: sets up the GUI window and elements, and creates a DeoVRClient for interacting with the DeoVR app.
        
        # Create two clients
        self.clients = [
            DeoVRClient(self, id=1),
            DeoVRClient(self, id=2)
        ]

        # Create main application window
        self.window = tk.Tk()
        self.window.title("DeoVR Remote Control")

        # Create "Connect" button and define what happens when it is clicked
        self.connect_button = tk.Button(self.window, text="Connect", command=self.connect_button_clicked)
        self.connect_button.pack()

        # Create "Disconnect" button and define what happens when it is clicked
        self.disconnect_button = tk.Button(self.window, text="Disconnect", command=self.disconnect_button_clicked)
        self.disconnect_button.pack()

        # Create and pack labels and entry fields for entering the hostname and port
        self.host_label = tk.Label(self.window, text="Hostname:")
        self.host_label.pack()
        self.hostname_entry = tk.Entry(self.window)
        self.hostname_entry.insert(0, '10.0.0.60')  # pre-fill with the default hostname
        self.hostname_entry.pack()

        self.port_label = tk.Label(self.window, text="Port:")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.window)
        self.port_entry.insert(0, '23554')  # pre-fill with the default port
        self.port_entry.pack()

        # Create and pack labels and entry field for entering the video path
        self.path_label = tk.Label(self.window, text="Video path:")
        self.path_label.pack()
        self.path_entry = tk.Entry(self.window)
        self.path_entry.pack()

        # Create "Open Path" button and define what happens when it is clicked
        self.open_path_button = tk.Button(self.window, text="Open Path", command=self.open_path_button_clicked)
        self.open_path_button.pack()

        # Create "Play" and "Pause" buttons and define what happens when they are clicked
        self.play_button = tk.Button(self.window, text="Play", command=self.play_button_clicked)
        self.play_button.pack()
        self.pause_button = tk.Button(self.window, text="Pause", command=self.pause_button_clicked)
        self.pause_button.pack()

        # Create label to display player status
        self.player_status = tk.Label(self.window, text="Player Status: Not Connected")
        self.player_status.pack()

        # Create labels to display the current time and duration of the video
        self.current_time_label = tk.Label(self.window, text="Current Time: 0.0")
        self.current_time_label.pack()
        self.duration_label = tk.Label(self.window, text="Duration: 0.0")
        self.duration_label.pack()

        # Create and pack label, entry field and button for the seek functionality
        self.seek_label = tk.Label(self.window, text="Seek to (in seconds):")
        self.seek_label.pack()
        self.seek_entry = tk.Entry(self.window)
        self.seek_entry.pack()
        self.seek_button = tk.Button(self.window, text="Seek", command=self.seek_button_clicked)
        self.seek_button.pack()

        # Create and pack label, entry field and button for the playback speed functionality
        self.playback_speed_label = tk.Label(self.window, text="Playback speed:")
        self.playback_speed_label.pack()
        self.playback_speed_entry = tk.Entry(self.window)
        self.playback_speed_entry.pack()
        self.set_playback_speed_button = tk.Button(self.window, text="Set Playback Speed", command=self.set_playback_speed_button_clicked)
        self.set_playback_speed_button.pack()

        # List of buttons that require a connection to work.
        self.buttons_that_require_connection = [
            self.open_path_button,
            self.play_button,
            self.pause_button,
            self.seek_button,
            self.set_playback_speed_button
        ]

        # Disable the buttons to start.
        self.set_buttons_state('disabled')


    def connect_button_clicked(self):
        try:
            hostname = self.hostname_entry.get()
            port = int(self.port_entry.get())
            for client in self.clients:
                client.connect(hostname, port)
            messagebox.showinfo("Connection status", "Successfully connected")
            # Enable the buttons when the connection is successful.
            self.set_buttons_state('normal')
        except Exception as e:
            messagebox.showerror("Connection status", f"Failed to connect: {e}")

    def disconnect_button_clicked(self):
        try:
            for client in self.clients:
                client.disconnect()
            messagebox.showinfo("Connection status", "Successfully disconnected")
            # Disable the buttons when the connection is closed.
            self.set_buttons_state('disabled')
        except Exception as e:
            messagebox.showerror("Connection status", f"Failed to disconnect: {e}")

    def set_buttons_state(self, state):
        """
        Set the state of all buttons that require a connection.

        :param state: The state to set. Should be either 'normal' or 'disabled'.
        """
        for button in self.buttons_that_require_connection:
            button.config(state=state)

    def open_path_button_clicked(self):
        path = self.path_entry.get()
        for client in self.clients:
            client.send({"path": path})

    def play_button_clicked(self):
        for client in self.clients:
            client.send({"playerState": 0})

    def pause_button_clicked(self):
        for client in self.clients:
            client.send({"playerState": 1})

    def seek_button_clicked(self):  # new method
        seek_time = float(self.seek_entry.get())  # we convert the input to float, as it's time in seconds
        for client in self.clients:
            client.send({"currentTime": seek_time})

    def set_playback_speed_button_clicked(self):
        playback_speed = float(self.playback_speed_entry.get())  # we convert the input to float, as it's speed
        for client in self.clients:
            client.send({"playbackSpeed": playback_speed})

    def update(self, data):
        print(f'Received data: {data}')  # This will log the data received.
        # Update GUI with received data
        player_state = "Playing" if data['playerState'] == 0 else "Paused"
        self.player_status["text"] = f"Player Status: {player_state}"

        if "currentTime" in data:
            self.current_time_label.config(text=f"Current Time: {data['currentTime']}")  # new

        if "duration" in data:
            self.duration_label.config(text=f"Duration: {data['duration']}")  # new

        if "playbackSpeed" in data:
            self.playback_speed_label.config(text=f"Playback Speed: {data['playbackSpeed']}") # new

    def stop_all_clients(self):
        for client in self.clients:
            client.stop()



    def run(self):
        self.window.mainloop()



if __name__ == "__main__":
    gui = DeoVRGui()
    atexit.register(gui.stop_all_clients)  # ensure stop is called when the program exits
    gui.run()