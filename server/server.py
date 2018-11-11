import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import socket
import errno
import json
import pygame
from game import maze, game_state
import network.message

import server_config
import config

PLAYERS = int(input('Number of players: '))            # amount of players
WEIGHT = server_config.WEIGHT

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
        client['socket'] = server_socket.accept()
        client['socket'][0].setblocking(False)
        print("Got connection from: " + str(client['socket'][1]))
    server_socket.close()
    return clients

def wait_nicknames(clients):
    count = 0
    while count < len(clients):
        for client in clients:
            if not 'name' in client:
                msg = network.message.recv_msg(client['socket'][0])
                msg = msg.decode()
            if msg:
                client['name'] = msg
                count += 1

def game_loop(clients):
    pygame.init()
    clock = pygame.time.Clock()

    for client in clients:
        client['time_since_update'] = 0
        client['illegal_move'] = False
        client['ema'] = server_config.MOVEMENT_TIMEOUT + 20

    time_since_transmission = 0

    while True:
        clock.tick(config.TICK_RATE)
        time_since_transmission += clock.get_time()

        # Read all sockets
        for client in clients:
            client['time_since_update'] += clock.get_time()
            if client['socket']:
                try:
                    buf = network.message.recv_msg(client['socket'][0])
                    if buf:
                        buf = buf.decode()
                        if buf:
                            client['ema'] = WEIGHT * client['ema'] + (1 - WEIGHT) * client['time_since_update']
                            if client['ema'] > server_config.MOVEMENT_TIMEOUT * 0.75:
                                client['illegal_movements'] = not game.from_json(buf)
                            else:
                                client['illegal_movements'] = True

                            client['time_since_update'] = 0
                except ConnectionResetError:
                    client['socket'] = None
                except (BlockingIOError, AttributeError):
                    pass


        if time_since_transmission > server_config.MOVEMENT_TIMEOUT:
            time_since_transmission = 0
            for client in clients:
                if client['socket']:
                    if client['illegal_move']:
                        encoded_message = str.encode(game.to_json())
                    else:
                        encoded_message = str.encode(game.to_json(client['id']))

                    network.message.send_msg(client['socket'][0], encoded_message)
                    client['illegal_move'] = False

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
    id_name_pairs.append((id_, client['name']))
    client['id'] = id_
    print(client['name'])

maze = maze.random_maze(config.GAME_WIDTH, server_config.MAP_COMPLEXITY, server_config.MAP_DENSITY, PLAYERS)
game = game_state.GameState(id_name_pairs, maze)

for player in game.players:
    for client in clients:
        if player.id == client['id']:
            client['player'] = player
            break

print("Sending maze data...")
# Send the maze to all clients
for client in clients:
    network.message.send_msg(client['socket'][0], str.encode(maze.as_json()))

print("Assigning player numbers...")
for client in clients:
    msg = dict([('player_number', client['id']), ('players', id_name_pairs)])
    network.message.send_msg(client['socket'][0], str.encode(json.dumps(msg)))

print("Starting game!")
game_loop(clients)
