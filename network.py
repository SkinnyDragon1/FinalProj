import socket
import dill as pickle
from typing import Union
from player import Human, Ghost, Player


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self) -> Player:
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(4096))
        except Exception as e:
            print("Error: " + str(e))

    def sendPlayer(self, data) -> Player:
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))

        except socket.error as e:
            print("Error: " + str(e))

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))

        except socket.error as e:
            print("Error: " + str(e))


