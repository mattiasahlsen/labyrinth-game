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
from game.maze import Maze

import network.message
import server_config
import config

import my_signals

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

def wait_backup_server():
    port = config.SERVER_PORT-1

    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(1.0)
            server_socket.bind((server_config.HOST, port))
            server_socket.listen(1)
            break
        except (socket.timeout, BlockingIOError):
            print('Timed out trying to listen for connections, trying again.')
        except OSError as e:
            #print('OSError, ')
            raise RuntimeError("Port:"+ str(port)+ "var upptagen")
            if e.errno == 48 or e.errno == 98: # address in use
                port += 1 # try with next port
            else:
                raise e

    print("Server listening on port " + str(port))
    while True:
        try:
            new_socket = server_socket.accept()
            break
        except socket.timeout:
            continue
    return new_socket[0]

def wait_clients(port):

    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(1.0)
            server_socket.bind((server_config.HOST, port))
            server_socket.listen(PLAYERS)
            break
        except (socket.timeout, BlockingIOError):
            print('Timed out trying to listen for connections, trying again.')
        except OSError as e:
            print(str(port))
            raise RuntimeError("Porten upptage upptagen")
            if e.errno == 48 or e.errno == 98: # address in use
                port += 1 # try with next port
            else:
                raise e

    print("Server listening on port " + str(port))

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
    print(len(clients))
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

def game_loop(clients, game, backup_server):
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
        
        if(backup_server):
            network.message.send_msg(backup_server, str.encode(game.to_json_name()))
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
        client[SOCKET][0].close()

def creating_backup_clients(clients):
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
        #send maze to backup
    else:
        for id_, client in enumerate(clients):
            player = game.players[id_]
def run_server(isBackupserver,game):

    #set 
    backup_server = None
    #wait for backup server to connect
    if(isBackupserver):
        pass
    else:
        backup_server = wait_backup_server()

    # Wait for all players to connect
    if(isBackupserver):
        clients = wait_clients(config.SERVER_PORT+10000)
    else:
        clients = wait_clients(config.SERVER_PORT)
        print(str(PLAYERS) + " players connected, waiting for nicknames...")

    if(isBackupserver):
        init_player_data = {}
        for client in clients:
            #Fill in client dict
            print("vi kom 1")
            buf = network.message.recv_msg(client[SOCKET][0])
            client['id']      = int(buf.decode())
            player = game.get_player(client['id'])
            client[PLAYER] = player
            client['name']    = player.name
            init_player_data[str(client['id'])] = player.serializable_init()

            
        #rcv id and add to each client
        #rcv name and add to each client
        #generate playerobject and add to each client
    else:
        wait_nicknames(clients)
        print('Received player names:')
        
    if(isBackupserver):
        pass
    else:
        maze = random_maze(config.GAME_WIDTH, server_config.MAP_COMPLEXITY, server_config.MAP_DENSITY, PLAYERS)
        game = GameState(maze)
        network.message.send_msg(backup_server, str.encode(maze.as_json()))
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
            #send maze to backup   
    game_loop(clients, game, backup_server)


def connect(ip, port):
    socket_to_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("hej")
    while True:
        try:
            try:
                socket_to_connect.connect((ip, port))
                break
            except(ConnectionRefusedError):
                print("failure")
                socket_to_connect.settimeout(1)
                time.sleep(5.5)
        except(ConnectionAbortedError):

            pass
    return socket_to_connect


def recive_infortmaion(server_socket, game):
    alive = True
    while alive:
        try:
            msg = network.message.recv_msg(server_socket)
            if msg:
                msg = msg.decode()
                data = json.loads(msg)
                if msg:
                    game.winners = data['winners']
                    players = data['players']
                    
                else:
                    pass
            else:
                print('main serverd ded')
                alive = False
        except ConnectionResetError:
            pass
    for player in players:
                        x = player['x']
                        y = player['y']
                        mId = player['id']
                        print('id givet på servern'+ str(mId))
                        name = player['name']
                        new_player = Player([x,y],name,None,mId)
                        game.add_player(new_player)
    return game

def wait_for_maze(server_socket):
    print('Waiting for maze')
    while True:
        msg = network.message.recv_msg(server_socket)
        if not msg:
            # try again in a sec (literally)
            print('Maze not received, trying again.')
            continue
        else:
            break
    print('Received maze.')
    maze = Maze(msg.decode())
    return maze
        
def backup_server():
    main_server_socket = connect(server_config.HOST, (config.SERVER_PORT-1))

    maze = wait_for_maze(main_server_socket)
    game = GameState(maze)
    
    print("Running backup server")
    game = recive_infortmaion(main_server_socket, game)
    run_server(True,game)
    

if(sys.argv[1] == "backup"):
    backup_server()
else:
    run_server(False, None)
