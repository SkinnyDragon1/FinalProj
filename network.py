import socket
import dill as pickle
from typing import Union, Tuple

from game import Game
from player import Human, Ghost, Player


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
        except Exception as e:
            print("Error: " + str(e))

    def getWaitingState(self):
        return pickle.loads(self.client.recv(4096))

    def send(self, data) -> Player:
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))

        except socket.error as e:
            print("Error: " + str(e))


