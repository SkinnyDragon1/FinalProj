import socket
from _thread import *
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


def threaded_client(conn: socket.socket, player, game_id) -> None:
    connected = True
    players = games[game_id].players
    while not games[game_id].connected():
        try:
            conn.send(pickle.dumps((players[player], games[game_id])))  # Keep pinging the first player until game is ready
            sleep(0.5)  # Sleep for half a second in order to not DOS player
        except ConnectionAbortedError:
            conn.close()  # Close connection
            print(f"Player {player} in game {game_id} has disconnected")
            games[game_id].crashed = True  # Update game as crashed
            return  # Stop the threaded client

    try:
        conn.send(pickle.dumps((players[player], games[game_id])))  # Send corrosponding player data to each player
    except ConnectionAbortedError:
        conn.close()  # Close connection
        print(f"Player {player} in game {game_id} has disconnected")
        games[game_id].crashed = True  # Update game as crashed
        return  # Stop the threaded client

    reply = ""
    while True:

        if games[game_id].crashed:
            print(f"Player {1- player} in game {game_id} has disconnected and therefore game has crashed")
            return

        try:
            data = pickle.loads(conn.recv(4096))  # Receive data

            if not (data.isHuman() or data.isGhost()):
                print(data)
                sleep(100)

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

        except EOFError:
            conn.close()  # Close connection
            print(f"Player {player} in game {game_id} has disconnected")
            games[game_id].crashed = True  # Update game as crashed
            return  # Stop the threaded client

    print("Lost Connection")
    conn.close()  # Close connection


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
