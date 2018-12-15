import sys
import os.path
import math
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import socket
import json
import pygame

from game.maze import random_maze
from game.game_state import GameState
from game.player import Player

import network.message
import server_config
import config

import my_signals
import atexit

EMA_WEIGHT = server_config.EMA_WEIGHT
MAX_SPEED = 1000 / config.MOVEMENT_TIMEOUT # squares per second

PLAYERS = None
while not PLAYERS:
    try:
        PLAYERS = int(input('Number of players (1-4): '))            # amount of players
        if (PLAYERS < 1 or PLAYERS > 4):
            print('Invalid number of players, try again.')
            PLAYERS = None
    except ValueError:
        print('Invalid input, try again.')

MAZE_WIDTH = None
try:
    while not MAZE_WIDTH:
        MAZE_WIDTH = int(input('Width in squares of maze (min 20, defaults to 51): '))
        if MAZE_WIDTH < 10:
            print('Maze width too low, must be at least 20. Try again.')
            MAZE_WIDTH = None
except ValueError:
    MAZE_WIDTH = config.GAME_WIDTH

print('Maze is size ' + str(MAZE_WIDTH) + 'x' + str(MAZE_WIDTH) + '.')

# Client dict keys
PLAYER = 'player'
NAME = 'name'
SOCKET = 'socket'
EMA = 'ema'
TIME_SINCE_UPDATE = 'time_since_update'
ILLEGAL_MOVE = 'illegal_move'
POSITIONS = 'positions'


def wait_clients():
    port = config.SERVER_PORT

    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.settimeout(1.0)
            server_socket.bind((server_config.HOST, config.SERVER_PORT))
            server_socket.listen(PLAYERS)
            break
        except (socket.timeout, BlockingIOError):
            print('Timed out trying to listen for connections, trying again.')
        except OSError as e:
            if e.errno == 48 or e.errno == 98: # address in use
                print('Address in use. Try waiting 20 seconds and then try again.')
                sys.exit()
            else:
                raise e

    print("Server listening on port " + str(port) + '. Waiting for clients to connect.')

    clients = []
    while len(clients) < PLAYERS:
        try:
            new_socket = server_socket.accept()
            client = {}
            clients.append(client)
            client[SOCKET] = new_socket
            client[SOCKET][0].setblocking(False)
            print("Got connection from: " + str(client[SOCKET][1]))
        except socket.timeout:
            continue

    print('Closing server socket.')
    server_socket.close()
    return clients

def get_nicknames(clients):
    count = 0
    while count < len(clients):
        for client in clients:
            if not NAME in client:
                msg = network.message.recv_msg(client[SOCKET][0])
                if not msg:
                    print('Error receiving username from client, exiting.')
                    sys.exit()
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
                    global PLAYERS

                    print(client[NAME] + ' disconnected and is now out of the game.')
                    PLAYERS -= 1
                    if PLAYERS == 0:
                        print('All players have disconnected, exiting.')
                        sys.exit()
                    client[SOCKET] = None

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
                print('Game is over, the winners are:')
                for winner in game.winners:
                    print(game.players[winner].name)
                break

    pygame.time.wait(3000)


# Wait for all players to connect
clients = wait_clients()
print(str(PLAYERS) + " players connected.")

def cleanup():
    print('Closing all client sockets.')
    for client in clients:
        if client[SOCKET] and client[SOCKET][0]:
            client[SOCKET][0].close()

atexit.register(cleanup)

get_nicknames(clients)
print('The players playing are: ', end='')
for i, client in enumerate(clients):
    print(client[NAME], end='')
    if not i == len(clients) - 1:
        print(', ', end='')
    else:
        print() # newline

maze = random_maze(MAZE_WIDTH, server_config.MAP_COMPLEXITY, server_config.MAP_DENSITY, PLAYERS)
game = GameState(maze)

for id_, client in enumerate(clients):
    player = Player(maze.starting_locations[id_], client[NAME])
    client['id'] = player.id
    client[PLAYER] = player
    game.add_player(player)

init_player_data = []
for _, player in game.players.items():
    init_player_data.append(player.serializable_init())


print("Sending maze data...")
# Send the maze to all clients
for client in clients:
    network.message.send_msg(client[SOCKET][0], str.encode(maze.as_json()))

print("Assigning player numbers...")
for client in clients:
    msg = dict([('id', client['id']), ('players', init_player_data)])
    network.message.send_msg(client[SOCKET][0], str.encode(json.dumps(msg)))

print("Starting game!")
game_loop(clients, game)
