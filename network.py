import socket
from struct import pack, unpack

import dill as pickle

from game import Game
from player import Player


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
        self.port: int = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self) -> None:
        try:
            self.client.connect(self.addr)
            # Connect to server address
        except Exception as e:
            print("Error: " + str(e))

    def load_server_data(self) -> (Player, Game):
        # Receive data from server
        try:
            prefix = self.client.recv(4, socket.MSG_WAITALL)  # Recieve first 4 bytes
        except OSError:
            print("Server is not online")
            return None

        print(prefix)

        length = unpack('!I', prefix)[0]  # Get length of incoming packet

        try:
            recieved = self.client.recv(length, socket.MSG_WAITALL)  # Recieve more bytes
        except OSError:
            print("Server is not online")
            return None

        print("Recieved packet of size: ", len(recieved))

        return pickle.loads(recieved)

    def send(self, data: Player) -> (Player, Game):
        try:
            packet = pickle.dumps(data)
            self.client.send(self.prefixed_packet(packet))  # Send pickled data
            return self.load_server_data()

        except socket.error as e:
            print("Error: " + str(e))

    @staticmethod
    def prefixed_packet(packet):
        length = pack('!I', len(packet))  # Get length of packet as packed bytes
        new_packet = length + packet  # Add length as prefix
        return new_packet  # Return packet with prefix
