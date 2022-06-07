import socket
from _thread import *
from time import sleep

from player import Player, Human, Ghost, default_players
import dill as pickle
from game import Game

server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("Waiting for connection - Server Started")

players = default_players
games = {}
idCount = 0

def threaded_client(conn: socket.socket, player, game_id):
    while not games[game_id].connected():
        conn.send(pickle.dumps((players[player], games[game_id])))
        sleep(0.5)
    conn.send(pickle.dumps((players[player], games[game_id])))

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


while True:
    connection, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    current_player = 0
    gameID = (idCount-1) // 2

    if idCount % 2 == 1:
        games[gameID] = Game(gameID)
        print(f'Creating a new game with id {gameID}')
    else:
        games[gameID].ready = True
        current_player = 1

    start_new_thread(threaded_client, (connection, current_player, gameID))
