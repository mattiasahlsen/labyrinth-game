import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import socket
import json
import pygame
import network.message
from graphics import renderer
from graphics import input_box
from game import game_state, maze

import client_config
import config

# Network constants
SERVER_IP = ''

# global variables
width = client_config.WINDOW_WIDTH

def connect(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    return client_socket

# Initialize pygame rendering and time-management
pygame.init()
screen = pygame.display.set_mode((width, width))
clock = pygame.time.Clock()

input_box = input_box.InputBox(width / 2, width / 2, 80, 'IP address')
renderer = renderer.Renderer(screen, width, input_box)

while True:
    clock.tick(client_config.FRAME_RATE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        SERVER_IP = input_box.handle_event(event)

    # Validate entered IP
    if SERVER_IP:
        if SERVER_IP == 'localhost':
            break
        try:
            socket.inet_aton(SERVER_IP)
            break
        except socket.error:
            continue

    renderer.render_connect_screen()
    pygame.display.flip()

screen.fill((0, 0, 0))
pygame.display.flip()

# Connect to server
client_socket = connect(SERVER_IP, config.SERVER_PORT)

# Wait for maze
msg = network.message.recv_msg(client_socket)
maze = maze.Maze(msg.decode())

# Wait for starting positions
msg = network.message.recv_msg(client_socket)
data = json.loads(msg.decode())
my_number = data['player_number']

# Game state object
game = game_state.LocalGameState(data['player_amount'], maze, my_number)
renderer.init_game(game)

velocity = (0, 0)
game_pos = game.players[my_number].current_pos()
tick_timeout = 0
client_socket.setblocking(False)

# Game loop
while 1:
    # Tick the clock
    clock.tick(client_config.FRAME_RATE)
    tick_timeout += clock.get_time()

    # Read data from the server
    try:
        msg = network.message.recv_msg(client_socket)
        if msg:
            msg = msg.decode()
            if msg:
                game.from_json(msg)
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
    if keys[pygame.K_RIGHT]:
        velocity = (1, 0)
    elif keys[pygame.K_LEFT]:
        velocity = (-1, 0)
    elif keys[pygame.K_UP]:
        velocity = (0, -1)
    elif keys[pygame.K_DOWN]:
        velocity = (0, 1)
    else:
        velocity = (0, 0)

    game.set_vel(my_number, velocity)

    if game_pos != game.players[my_number].current_pos():
        game_pos = game.players[my_number].current_pos()
        network.message.send_msg(client_socket, str.encode(game.to_json()))

    # Send updates to server every TICK_INTERVAL milliseconds
    if tick_timeout > client_config.TICK_INTERVAL:
        tick_timeout = 0

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    pygame.display.flip()
