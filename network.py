import socket
import dill as pickle
from player import Player
from struct import pack, unpack


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

    def load_server_data(self):
        # Receive data from server
        prefix = self.client.recv(4, socket.MSG_WAITALL)

        length = unpack('!I', prefix)[0]  # Get length of incoming packet

        recieved = self.client.recv(length)  # Recieve more bytes
        print(len(recieved), recieved)

        return pickle.loads(recieved)

    def send(self, data) -> Player:
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


