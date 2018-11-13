import sys
import os.path
import math
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import socket
import json
import pygame
from game import maze, game_state
import network.message

import server_config
import config

EMA_WEIGHT = server_config.EMA_WEIGHT
MAX_SPEED = 1000 / config.MOVEMENT_TIMEOUT # squares per second

PLAYERS = int(input('Number of players: '))            # amount of players

# Client dict keys
PLAYER = 'player'
NAME = 'name'
SOCKET = 'socket'
EMA = 'ema'
TIME_SINCE_UPDATE = 'time_since_update'
ILLEGAL_MOVE = 'illegal_move'
POSITIONS = 'positions'

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
        client = {}
        clients.append(client)
        client[SOCKET] = server_socket.accept()
        client[SOCKET][0].setblocking(False)
        print("Got connection from: " + str(client[SOCKET][1]))
    server_socket.close()
    return clients

def wait_nicknames(clients):
    count = 0
    while count < len(clients):
        for client in clients:
            if not NAME in client:
                msg = network.message.recv_msg(client[SOCKET][0])
                msg = msg.decode()
            if msg:
                client[NAME] = msg
                count += 1

# used for weighting average
# get avg speed in squares per second
def avg_speed(e1, e2):
    dx, dy, dt = e2[0] - e1[0], e2[1] - e1[1], (e2[2] - e1[2]) / 1000
    return math.sqrt(dx**2 + dy**2) / dt

def game_loop(clients, game):
    pygame.init()
    clock = pygame.time.Clock()

    for client in clients:
        client[TIME_SINCE_UPDATE] = 0
        client[ILLEGAL_MOVE] = False
        client[EMA] = MAX_SPEED * (1 - server_config.SPEED_MARGIN)
        client[POSITIONS] = [(client[PLAYER].x, client[PLAYER].y, 0)] * server_config.COLLECTED_MOVES

    time_since_transmission = 0

    while True:
        clock.tick(server_config.TICK_RATE)
        time_since_transmission += clock.get_time()

        # Read all sockets
        for client in clients:
            client[TIME_SINCE_UPDATE] += clock.get_time()
            if client[SOCKET]:
                try:
                    buf = network.message.recv_msg(client[SOCKET][0])
                    if buf and buf.decode():
                        buf = buf.decode()

                        p = client[PLAYER]
                        client[POSITIONS].append((p.x, p.y, pygame.time.get_ticks()))
                        client[POSITIONS].pop(0)
                        new_avg_speed = avg_speed(
                            client[POSITIONS][0],
                            client[POSITIONS][-1]
                        )
                        client[EMA] = EMA_WEIGHT * client[EMA] + (1 - EMA_WEIGHT) * new_avg_speed
                        if client[EMA] < MAX_SPEED * (1 + server_config.SPEED_MARGIN):
                            client[ILLEGAL_MOVE] = not game.from_json(buf)
                        else:
                            client[ILLEGAL_MOVE] = True

                        client[TIME_SINCE_UPDATE] = 0
                except ConnectionResetError:
                    client[SOCKET] = None
                except (BlockingIOError, AttributeError):
                    pass

        if time_since_transmission > config.MOVEMENT_TIMEOUT:
            time_since_transmission = 0
            for client in clients:
                if client[SOCKET]:
                    if client[ILLEGAL_MOVE]:
                        encoded_message = str.encode(game.to_json())
                    else:
                        encoded_message = str.encode(game.to_json(client['id']))

                    network.message.send_msg(client[SOCKET][0], encoded_message)
                    client[ILLEGAL_MOVE] = False

            if game.winners:
                break

    pygame.time.wait(3000)
    for client in clients:
        client[0].close()


# Wait for all players to connect
clients = wait_players()
print(str(PLAYERS) + " players connected, waiting for nicknames...")

wait_nicknames(clients)
print('Received player names:')

id_name_pairs = []
for id_, client in enumerate(clients):
    id_name_pairs.append((id_, client[NAME]))
    client['id'] = id_

maze = maze.random_maze(config.GAME_WIDTH, server_config.MAP_COMPLEXITY, server_config.MAP_DENSITY, PLAYERS)
game = game_state.GameState(id_name_pairs, maze)

for player in game.players:
    for client in clients:
        if player.id == client['id']:
            client[PLAYER] = player
            break

print("Sending maze data...")
# Send the maze to all clients
for client in clients:
    network.message.send_msg(client[SOCKET][0], str.encode(maze.as_json()))

print("Assigning player numbers...")
for client in clients:
    msg = dict([('player_number', client['id']), ('players', id_name_pairs)])
    network.message.send_msg(client[SOCKET][0], str.encode(json.dumps(msg)))

print("Starting game!")
game_loop(clients, game)
