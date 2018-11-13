import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import math
import socket
import json
import pygame
import network.message
from graphics import renderer

from local_game_state import LocalGameState
from game import maze

import client_config
import config

def connect(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    return client_socket

# Game constants
DISPLAY_PARAMS = pygame.RESIZABLE
PLAYER_NAME = input('Nickname: ')

# Network constants
SERVER_IP = input('IP of server: ')

# Connect to server
client_socket = connect(SERVER_IP, config.SERVER_PORT)

network.message.send_msg(client_socket, str.encode(PLAYER_NAME))

# Wait for maze
msg = network.message.recv_msg(client_socket)
maze = maze.Maze(msg.decode())

RES = client_config.RESOLUTION

# Initialize pygame rendering and time-management
pygame.init()
screen = pygame.display.set_mode((RES, RES), DISPLAY_PARAMS)
clock = pygame.time.Clock()

# Wait for starting positions
msg = network.message.recv_msg(client_socket)
data = json.loads(msg.decode())
my_number = data['player_number']
id_name_pairs = data['players']

# Game state object
game = LocalGameState(id_name_pairs, maze, my_number, RES / client_config.VIEW_DISTANCE)
renderer = renderer.Renderer(screen, RES, game, )

velocity = (0, 0)
game_pos = game.players[my_number].current_pos()
client_socket.setblocking(False)

# Game loop
while 1:
    clock.tick(client_config.FRAME_RATE)
    game.tick()
    # Read data from the server
    try:
        msg = network.message.recv_msg(client_socket)
        if msg:
            msg = msg.decode()
            if msg:
                game.from_json(msg)
    except ConnectionResetError:
        pass
    except BlockingIOError:
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

    game.set_vel(my_number, velocity)

    if game_pos != game.players[my_number].current_pos():
        game_pos = game.players[my_number].current_pos()
        network.message.send_msg(client_socket, str.encode(game.to_json()))

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            RES = min(event.w, event.h)
            game = LocalGameState(id_name_pairs, maze, my_number, RES / client_config.VIEW_DISTANCE)
            renderer = renderer.update_res(RES / client_config.VIEW_DISTANCE, game)

    pygame.display.flip()
