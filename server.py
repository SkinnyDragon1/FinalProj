import socket
from _thread import *
from player import Player, Human, Ghost
from time import time
# noinspection PyUnresolvedReferences
import dill as pickle
# import pickle
import sys

server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("Waiting for connection - Server Started")

players = [Human(1, 1, "off", 0, lives=3), Ghost(100, 100, health=100, timer=time(), burning=False)]


def threaded_client(conn, player):
    conn.send(pickle.dumps(players[player]))

    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            players[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = players[0]
                else:
                    reply = players[1]

                print("Recieved: ", data)
                print("Sending: ", reply)

            conn.sendall(pickle.dumps(reply))

        except:
            break

    print("Lost Connection")
    conn.close()


current_player = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, current_player))
    current_player += 1
