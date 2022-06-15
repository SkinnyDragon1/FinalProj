import socket
from _thread import *
from time import sleep
from player import default_players
import dill as pickle
from game import Game

server = socket.gethostbyname(socket.gethostname())  # "192.168.1.42"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Initialize socket with constants as arguments

try:
    s.bind((server, port))  # Bind server to port
except socket.error as e:
    print(str(e))

s.listen()  # Begin listening for connections
print("Waiting for connection - Server Started")

players = default_players  # Get the default player's data
games = {}  # Keep track of games
idCount = 0  # Keep track of game IDs

def threaded_client(conn: socket.socket, player, game_id):
    while not games[game_id].connected():
        conn.send(pickle.dumps((players[player], games[game_id])))  # Keep pinging the first player until game is ready
        sleep(0.5)  # Sleep for half a second in order to not DOS player
    conn.send(pickle.dumps((players[player], games[game_id])))  # Send corrosponding player data to each player

    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(4096))  # Receive data
            players[player] = data  # Update database

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

            conn.sendall(pickle.dumps(reply))  # Send opposing players data

        except Exception as ex:
            print(ex)

    print("Lost Connection")
    conn.close()  # Close connection


while True:
    connection, addr = s.accept()  # Accept connections to server
    print("Connected to:", addr)

    idCount += 1  # Increment idCount
    current_player = 0  # Player 1
    gameID = (idCount-1) // 2  # Calculate game id so that every 2 players connect to the same game id

    if idCount % 2 == 1:  # First player to connect
        games[gameID] = Game(gameID)  # Create new game
        print(f'Creating a new game with id {gameID}')
    else:
        games[gameID].ready = True  # Connect to already created game and update it to start the game
        current_player = 1

    start_new_thread(threaded_client, (connection, current_player, gameID))  # Create new thread
