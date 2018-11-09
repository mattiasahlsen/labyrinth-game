import sys
import socket
import json
import pygame
import network.message
from game import *
from graphics import renderer

# Network constants
SERVER_IP = 'localhost'
SERVER_PORT = 15000
TICK_INTERVAL = 50

# Game constants
width = 560
FRAME_RATE = 120

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Wait for maze
msg = network.message.recv_msg(client_socket)
maze = maze.Maze(msg.decode())

# Wait for starting positions
msg = network.message.recv_msg(client_socket)
data = json.loads(msg.decode())

# Game state object
game = game_state.Game_State(data['player_amount'], maze)

# Initialize pygame rendering and time-management
pygame.init()
screen = pygame.display.set_mode((width, width))
renderer = renderer.Renderer(screen, width, game)
clock = pygame.time.Clock()

velocity = (0, 0)
tick_timeout = 0
client_socket.setblocking(False)

# Game loop
while 1:
    # Tick the clock
    clock.tick(FRAME_RATE)
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
        renderer.render()

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

    # Send updates to server every TICK_INTERVAL milliseconds
    if tick_timeout > TICK_INTERVAL and velocity != (0, 0):
        network.message.send_msg(client_socket, str.encode(json.dumps(velocity)))
        tick_timeout = 0

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    pygame.display.flip()
    