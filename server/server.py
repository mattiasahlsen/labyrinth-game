import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import socket
import json
import pygame
from game import maze, game_state
import network.message

import server_config
import config

PLAYERS = int(input('Number of players: '))            # amount of players

def wait_players():
    port = config.SERVER_PORT

    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((server_config.HOST, config.SERVER_PORT))
            server_socket.listen(PLAYERS)
            break
        except OSError as e:
            if e.errno == 48: # address in use
                port += 1 # try with next port
            else:
                raise e

    print("Server listening on port " + str(port))

    clients = []
    while len(clients) < PLAYERS:
        clients.append(server_socket.accept())
        clients[-1][0].setblocking(False)
        print("Got connection from: " + str(clients[-1][1]))
    server_socket.close()
    return clients

def wait_nicknames():
    names = dict()

    while len(names) < PLAYERS:
        for i in range(len(clients)):
            msg = network.message.recv_msg(clients[i][0])
            msg = msg.decode()
            if msg:
                names[i] = msg
    return names

def game_loop():
    pygame.init()
    clock = pygame.time.Clock()

    time_since_transmission = 0
    time_since_update = dict()
    illegal_movements = dict()      # if any value is set in this dictionary, the client has moved illegaly
    ma = []                         # moving averages of time between packets for all clients
    for i in range(PLAYERS):
        time_since_update[i] = 0
        illegal_movements[i] = False
        ma.append(server_config.MOVEMENT_TIMEOUT + 20)

    while True:
        # Time
        clock.tick(config.TICK_RATE)
        for i in range(PLAYERS):
            time_since_update[i] += clock.get_time()
        time_since_transmission += clock.get_time()
        # Read all sockets
        for i in range(PLAYERS):
            try:
                buf = network.message.recv_msg(clients[i][0])
                buf = buf.decode()
                if buf:
                    ma[i] = 0.75 * ma[i] + 0.25 * time_since_update[i]
                    if ma[i] > server_config.MOVEMENT_TIMEOUT:
                        illegal_movements[i] = not game.from_json(buf)
                    else:
                        illegal_movements[i] = True
                    time_since_update[i] = 0
            except BlockingIOError:
                pass

        if time_since_transmission > server_config.MOVEMENT_TIMEOUT:
            time_since_transmission = 0
            for i in range(PLAYERS):
                if illegal_movements[i]:
                    encoded_message = str.encode(game.to_json())
                else:
                    encoded_message = str.encode(game.to_json(i))

                network.message.send_msg(clients[i][0], encoded_message)
                illegal_movements[i] = False

            if game.winners:
                break

    pygame.time.wait(3000)
    for client in clients:
        client[0].close()


# Wait for all players to connect
clients = wait_players()
print(str(PLAYERS) + " players connected, waiting for nicknames...")

names = wait_nicknames()
print('Received player names: ' + str(names))

maze = maze.random_maze(config.GAME_WIDTH, server_config.MAP_COMPLEXITY, server_config.MAP_DENSITY, PLAYERS)
game = game_state.GameState(names, maze)

print("Sending maze data...")
# Send the maze to all clients
for client in clients:
    network.message.send_msg(client[0], str.encode(maze.as_json()))

print("Assigning player numbers...")
i = 0
for client in clients:
    msg = dict([('player_number', i), ('players', names)])
    network.message.send_msg(client[0], str.encode(json.dumps(msg)))
    i += 1

print("Starting game!")
game_loop()
