import socket
import dill as pickle
from player import Player


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            # Connect to server address
        except Exception as e:
            print("Error: " + str(e))

    def getWaitingState(self):
        # Receive data from server
        return pickle.loads(self.client.recv(4096))

    def send(self, data) -> Player:
        try:
            self.client.send(pickle.dumps(data))  # Send pickled data
            return pickle.loads(self.client.recv(4096))  # Receive pickled data

        except socket.error as e:
            print("Error: " + str(e))


