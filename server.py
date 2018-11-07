import socket, game.maze

def wait_players():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)

    clients = []
    while len(clients) < PLAYERS:
        clients.append(server_socket.accept())
        print("Got connection from: " + str(clients[-1][1]))
    return clients

        
# Networking constants
HOST = ''
PORT = 15000

# Game related
PLAYERS = 1
maze = game.maze.Maze(None, None)

# Wait for all players to connect
clients = wait_players()
# Send the maze to all clients
for client in clients:    
    client[0].send(str.encode(maze.as_json()))


