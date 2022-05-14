import socket
import pickle
from typing import Union
from player import Human, Ghost


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self) -> Union[Human, Ghost]:
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))

        except socket.error as e:
            print("Error: " + str(e))

# n = Network()
# print(n.send("hello"))
# print(n.send("working"))
# print(n.getPos())
