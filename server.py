from game import *
import socket, pygame, json

def wait_players():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)

    clients = []
    while len(clients) < PLAYERS:
        clients.append(server_socket.accept())
        clients[-1][0].setblocking(False)
        print("Got connection from: " + str(clients[-1][1]))
    return clients

def game_loop():
    pygame.init()
    clock = pygame.time.Clock()
    time_since_movement = 0

    velocities = dict()
    for i in range(PLAYERS):
        velocities[i] = (0, 0)

    while True:
        # Time
        clock.tick(40)  
        time_since_movement += clock.get_time()

        # Read all sockets
        for i in range(PLAYERS):
            try:
                buf = clients[i][0].recv(BUF_SIZ)
                buf = buf.decode()
                if buf:
                    velocities[i] = json.loads(buf)
            except BlockingIOError:
                pass

        if time_since_movement > MOVEMENT_TIMEOUT:
            for i in range(PLAYERS):
                print("i: " + str(i) + ", vel: " + str(velocities[i]))
                game.set_vel(i, velocities[i])

            print("Game state: " + str(game.state_as_json()))

            game.tick()
            time_since_movement = 0
            for i in range(PLAYERS):
                clients[i][0].send(str.encode(game.state_as_json()))
                velocities[i] = (0, 0)
        
# Networking constants
HOST = ''
PORT = 15000
BUF_SIZ = 1024

# Game related
PLAYERS = 1     # amount of players
MOVEMENT_TIMEOUT = 100  # timeout for moving one unit

maze = maze.Maze()
game = game_state.Game_State(PLAYERS, maze)

# Wait for all players to connect
clients = wait_players()
print(str(PLAYERS) + " players connected, sending maze data...")

# Send the maze to all clients
for client in clients:    
    client[0].send(str.encode(maze.as_json()))

print("Assigning player numbers...")
i = 0
for client in clients:
    msg = dict([('player_number', i), ('player_amount', PLAYERS)])
    client[0].send(str.encode(json.dumps(msg)))
    i += 1

print("Starting game!")
game_loop()