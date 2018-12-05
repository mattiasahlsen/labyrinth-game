import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import time
import math
import socket
import json
import pygame
import network.message
from graphics import renderer

from local_game_state import LocalGameState
from game import maze

from game.player import LocalPlayer, Player

import client_config
import config

def connect(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    client_socket.settimeout(1)
    return client_socket

# Game constants
DISPLAY_PARAMS = 0
PLAYER_NAME = input('Nickname: ')

# Network constants
SERVER_IP = input('IP of server: ')

# Connect to server
client_socket = connect(SERVER_IP, config.SERVER_PORT)

network.message.send_msg(client_socket, str.encode(PLAYER_NAME))

# Wait for maze
print('Waiting for maze')
while True:
    msg = network.message.recv_msg(client_socket)

    if not msg:
        # try again in a sec (literally)
        print('Maze not received, trying again.')
        continue
    else:
        if str(msg.decode()) == "no":
            print("not ok name")
            sys.exit()
        break
print('Received maze.')
maze = maze.Maze(msg.decode())

RES = client_config.RESOLUTION

# Initialize pygame rendering and time-management
pygame.init()
screen = pygame.display.set_mode((RES, RES), DISPLAY_PARAMS)
clock = pygame.time.Clock()

# Wait for player data
while True:
    msg = network.message.recv_msg(client_socket)
    if not msg:
        print('Player data not received, trying again')
        continue
    else:
        break
client_socket.setblocking(False)

data = json.loads(msg.decode())
my_id = data['id']
players = []
for player in data['players']:
    if player['id'] == my_id:
        players.append(LocalPlayer((player['x'], player['y']),
                                    player['name'], player['avatar']))
    else:
        players.append(Player((player['x'], player['y']),
                                    player['name'], player['avatar']))

# Game state object
game = LocalGameState(maze, players, my_id, RES / client_config.VIEW_DISTANCE)
renderer = renderer.Renderer(screen, RES, game)

velocity = (0, 0)
my_pos = game.players[my_id].current_pos()

# Game loop
while 1:
    clock.tick(client_config.FRAME_RATE)
    game.tick(clock.get_fps())
    # Read data from the server
    try:
        msg = network.message.recv_msg(client_socket)
        if msg:
            msg = msg.decode()
            if msg:
                game.from_json(msg)
    except ConnectionResetError:
        # do something here later, maybe reconnect?
        pass

    # Render graphics
    if game.winners:
        renderer.finish()
    else:
        renderer.render_game()

    # Keyboard input
    pygame.event.pump()
    keys = pygame.key.get_pressed()

    diag = False
    if ( (keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]) and
         (keys[pygame.K_UP] or keys[pygame.K_DOWN]) ):
        diag = True
    velocity = (0, 0)
    if keys[pygame.K_RIGHT]:
        if diag:
            velocity = (math.sqrt(0.5), velocity[1])
        else:
            velocity = (1, 0)
    elif keys[pygame.K_LEFT]:
        if diag:
            velocity = (-math.sqrt(0.5), velocity[1])
        else:
            velocity = (-1, 0)
    if keys[pygame.K_UP]:
        if diag:
            velocity = (velocity[0], -math.sqrt(0.5))
        else:
            velocity = (0, -1)
    elif keys[pygame.K_DOWN]:
        if diag:
            velocity = (velocity[0], math.sqrt(0.5))
        else:
            velocity =  (0, 1)
    elif keys[pygame.K_h] and keys[pygame.K_a] and keys[pygame.K_x]:
        # Activate hax
        game.players[game.local_player].x = maze.goal[0]
        game.players[game.local_player].y = maze.goal[1]
        network.message.send_msg(client_socket, str.encode(game.to_json()))

    game.set_vel(my_id, velocity)

    if my_pos != game.players[my_id].current_pos():
        my_pos = game.players[my_id].current_pos()
        network.message.send_msg(client_socket, str.encode(game.to_json()))

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            """
                RES = min(event.w, event.h)
                game = LocalGameState(id_name_pairs, maze, my_id, RES / client_config.VIEW_DISTANCE)
                renderer = renderer.update_res(RES / client_config.VIEW_DISTANCE, game)
            """

    pygame.display.flip()
