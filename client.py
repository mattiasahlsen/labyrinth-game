from game import *
from graphics import renderer
import pygame, sys, socket, json

# Network constants
SERVER_IP = 'localhost'
SERVER_PORT = 15000
TICK_INTERVAL = 50

# Game constants
width = 560

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, SERVER_PORT))

# Connected, waiting for maze to be sent
BUF_SIZ = 1024 * 20

while True:
    buf = s.recv(BUF_SIZ)
    if buf.decode():
        break

buf = buf.decode()
maze = maze.Maze(buf)

# Waiting for initial positions
BUF_SIZ = 1024 * 4
while True:
    buf = s.recv(BUF_SIZ)
    if buf.decode():
        break

buf = buf.decode()
data = json.loads(buf)
player_amount = data['player_amount']
my_player = data['player_number']

# Game state object
game = game_state.Game_State(player_amount, maze)

pygame.init()
block_size = width / maze.width
screen = pygame.display.set_mode((width, width))
renderer = renderer.Renderer(screen, width, game)
clock = pygame.time.Clock()

BUF_SIZ = 1024
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
        buf = s.recv(BUF_SIZ)
        buf = buf.decode()
        if buf:
            game.from_json(buf)
    except BlockingIOError:
        pass

    # Handle exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # Render graphics
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
    
    if tick_timeout > TICK_INTERVAL and vel != (0, 0):
        s.send(str.encode(json.dumps(vel)))
        tick_timeout = 0

    pygame.display.flip()