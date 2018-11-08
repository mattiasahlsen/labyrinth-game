from game import *
from graphics import renderer
import pygame, sys, socket, json, network.message

# Network constants
SERVER_IP = 'localhost'
SERVER_PORT = 15000
TICK_INTERVAL = 50

# Game constants
width = 560

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, SERVER_PORT))

# Wait for maze
while True:
    buf = network.message.recv_msg(s)
    if buf.decode():
        break
maze = maze.Maze(buf.decode())

# Waiting for initial positions
while True:
    buf = network.message.recv_msg(s)
    if buf.decode():
        break

data = json.loads(buf.decode())
player_amount = data['player_amount']
my_player = data['player_number']

# Game state object
game = game_state.Game_State(player_amount, maze)

# Initialize pygame rendering and time-management
pygame.init()
block_size = width / maze.width
screen = pygame.display.set_mode((width, width))
renderer = renderer.Renderer(screen, width, game)
clock = pygame.time.Clock()

vel = (0, 0)
tick_timeout = 0
s.setblocking(False)

# Game loop
while 1:
    # Tick the clock
    clock.tick(120)
    tick_timeout += clock.get_time()

    # Read data from the server
    try:
        buf = network.message.recv_msg(s)
        if buf:
            buf = buf.decode()
            if buf:
                game.from_json(buf)
    except BlockingIOError:
        pass

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    if len(game.winners) > 0:
        renderer.finish()
    else:
        renderer.render()
    

    # Keyboard input
    pygame.event.pump()
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_RIGHT]):
        vel = (1, 0)
    elif (keys[pygame.K_LEFT]):
        vel = (-1, 0)
    elif (keys[pygame.K_UP]):
        vel = (0, -1)
    elif (keys[pygame.K_DOWN]):
        vel = (0, 1)
    else:
        vel = (0, 0)
    
    # Send updates to server every TICK_INTERVAL milliseconds
    if tick_timeout > TICK_INTERVAL and vel != (0, 0):
        network.message.send_msg(s, str.encode(json.dumps(vel)))
        tick_timeout = 0

    pygame.display.flip()