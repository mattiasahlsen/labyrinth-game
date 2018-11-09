import socket
import json
import pygame
from game import *
import network.message

# Networking constants
HOST = ''
PORT = 15000

# Game related
print('Amount of players: ', end='')
PLAYERS = int(input())            # amount of players
MOVEMENT_TIMEOUT = 50   # timeout for moving one unit
TICK_RATE = 40          # server ticks per second

def wait_players():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(PLAYERS)

    clients = []
    while len(clients) < PLAYERS:
        clients.append(server_socket.accept())
        clients[-1][0].setblocking(False)
        print("Got connection from: " + str(clients[-1][1]))
    server_socket.close()
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
        clock.tick(TICK_RATE)
        time_since_movement += clock.get_time()

        # Read all sockets
        for i in range(PLAYERS):
            try:
                buf = network.message.recv_msg(clients[i][0])
                buf = buf.decode()
                if buf:
                    velocities[i] = json.loads(buf)
            except BlockingIOError:
                pass

        if time_since_movement > MOVEMENT_TIMEOUT:
            for i in range(PLAYERS):
                game.set_vel(i, velocities[i])

            print("Game state: " + str(game.state_as_json()))

            game.tick()
            time_since_movement = 0
            for i in range(PLAYERS):
                network.message.send_msg(clients[i][0], str.encode(game.state_as_json()))
                velocities[i] = (0, 0)

            if game.winners:
                break

    pygame.time.wait(3000)
    for client in clients:
        client[0].close()

maze = maze.random_maze()
game = game_state.Game_State(PLAYERS, maze)

# Wait for all players to connect
clients = wait_players()
print(str(PLAYERS) + " players connected, sending maze data...")

# Send the maze to all clients
for client in clients:
    network.message.send_msg(client[0], str.encode(maze.as_json()))

print("Assigning player numbers...")
i = 0
for client in clients:
    msg = dict([('player_number', i), ('player_amount', PLAYERS)])
    network.message.send_msg(client[0], str.encode(json.dumps(msg)))
    i += 1

print("Starting game!")
game_loop()
