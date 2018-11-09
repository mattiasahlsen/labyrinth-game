import sys
import socket
import json
import pygame
import network.message
from graphics import renderer
from graphics import input_box
from game import game_state, maze

# Network constants
SERVER_IP = ''
SERVER_PORT = 15000
TICK_INTERVAL = 50

# Game constants
width = 560
FRAME_RATE = 120

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
    clock.tick(FRAME_RATE)
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
client_socket = connect(SERVER_IP, SERVER_PORT)

# Wait for maze
msg = network.message.recv_msg(client_socket)
maze = maze.Maze(msg.decode())

# Wait for starting positions
msg = network.message.recv_msg(client_socket)
data = json.loads(msg.decode())
my_number = data['player_number']

# Game state object
game = game_state.Game_State(data['player_amount'], maze)
renderer.init_game(game)

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

    # Send updates to server every TICK_INTERVAL milliseconds
    if tick_timeout > TICK_INTERVAL and velocity != (0, 0):
        network.message.send_msg(client_socket, str.encode(json.dumps(velocity)))
        game.set_vel(my_number, velocity)
        game.tick()
        tick_timeout = 0

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    pygame.display.flip()
