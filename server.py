import socket
import struct
from _thread import *
from struct import pack, unpack
from time import sleep

import dill as pickle

from game import Game
from player import human_spawnpoint, ghost_spawnpoint, Human, Ghost

server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Initialize socket with constants as arguments

try:
    s.bind((server, port))  # Bind server to port
except socket.error as e:
    print(str(e))

s.listen()  # Begin listening for connections
print("Waiting for connection - Server Started")

games = {}  # Keep track of games
idCount = 0  # Keep track of game IDs


def prefixed_packet(packet):
    length = pack('!I', len(packet))  # Get length of packet as packed bytes
    new_packet = length + packet  # Add length as prefix
    return new_packet  # Return packet with prefix


def load_prefixed_data(conn: socket.socket):
    prefix = conn.recv(4, socket.MSG_WAITALL)

    length = unpack('!I', prefix)[0]  # Get length of incoming packet

    recieved = conn.recv(length)  # Recieve more bytes
    print("Recieved packet of size: ", len(recieved))

    return pickle.loads(recieved)


def threaded_client(conn: socket.socket, player, game_id) -> None:
    players = games[game_id].players
    while not games[game_id].connected():
        try:
            packet = pickle.dumps((players[player], games[game_id]))  # Set up packet for sending
            print(f'packet being sent to player {player}')
            conn.send(prefixed_packet(packet))  # Keep pinging the first player until game is ready
            sleep(0.5)  # Sleep for half a second in order to not DOS player
        except ConnectionAbortedError:

            conn.close()  # Close connection
            print(f"Player {player} in game {game_id} has disconnected")
            games[game_id].crashed = True  # Update game as crashed
            return  # Stop the threaded client

    try:
        packet = pickle.dumps((players[player], games[game_id]))
        print(f'packet being sent to player {player}')
        conn.send(prefixed_packet(packet))  # Send corresponding  player data to each player
    except ConnectionAbortedError:
        conn.close()  # Close connection
        print(f"Player {player} in game {game_id} has disconnected")
        games[game_id].crashed = True  # Update game as crashed
        return  # Stop the threaded client

    reply = ""
    while True:

        if games[game_id].crashed:
            print(f"Player {1 - player} in game {game_id} has disconnected and therefore game has crashed")
            return  # Stop the threaded client

        try:
            data = load_prefixed_data(conn)  # Receive data

            print(data)

            players[player] = data  # Update database

            reply = players[1 - player]  # Load response

            print("Recieved: ", data)
            print("Sending: ", reply)

            packet = pickle.dumps((reply, games[game_id]))  # Set up packet for sending
            conn.sendall(prefixed_packet(packet))  # Send opposing players data

        except (EOFError, struct.error):
            conn.close()  # Close connection
            print(f"Player {player} in game {game_id} has disconnected")
            games[game_id].crashed = True  # Update game as crashed
            return  # Stop the threaded client


while True:
    connection, addr = s.accept()  # Accept connections to server
    print("Connected to:", addr)

    idCount += 1  # Increment idCount
    current_player = 0  # Player 1
    gameID = (idCount - 1) // 2  # Calculate game id so that every 2 players connect to the same game id

    if idCount % 2 == 1:  # First player to connect
        games[gameID] = Game(gameID, default_players=[Human(human_spawnpoint[0], human_spawnpoint[1]),
                                                      Ghost(ghost_spawnpoint[0],
                                                            ghost_spawnpoint[1])])  # Create new game
        print(f'Creating a new game with id {gameID}')
    else:
        games[gameID].ready = True  # Connect to already created game and update it to start the game
        current_player = 1

    start_new_thread(threaded_client, (connection, current_player, gameID))  # Create new thread
