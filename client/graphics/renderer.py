import math
import pygame
from graphics.colors import *

from config import GAME_WIDTH
from client_config import FRAME_RATE, TICK_INTERVAL, WINDOW_WIDTH

# globals
FRAMES_PER_TICK = TICK_INTERVAL / (1000 / FRAME_RATE)

class Renderer:
    def __init__(self, screen, res, input_box):
        self.screen = screen
        self.res = res
        self.input_box = input_box
        self.block_size = None
        self.game = None
        self.maze = None
        self.width = None
        self.pixel_positions = []

    def render_connect_screen(self):
        self.screen.fill(BACKGROUND)
        self.input_box.update()
        self.input_box.draw(self.screen)

    def init_game(self, game_state):
        self.game = game_state
        self.maze = self.game.maze
        self.width = self.maze.width
        self.block_size = self.res / self.width
        self.pixels_per_frame = 1000 * self.block_size / (FRAME_RATE * TICK_INTERVAL)
        self.pixel_positions = [None] * len(game_state.players)
        self.local_player = game_state.local_player

        for player in game_state.players:
            self.pixel_positions[player.player_number] = self.to_pixels((player.x, player.y))
            

    def render_game(self):
        self.screen.fill(BLACK)
        maze_walls = []
        for y in range(self.width):
            for x in range(self.width):
                if self.maze.maze[y * self.width + x]:
                    col = WHITE
                    maze_walls.append(
                       pygame.draw.rect(self.screen, col, (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 0)
                    )
                else: 
                    col = BLACK
                    pygame.draw.rect(self.screen, col, (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 0)
                

        pygame.draw.rect(self.screen, YELLOW,
                        (self.maze.goal[0] * self.block_size, self.maze.goal[1] * self.block_size, self.block_size, self.block_size), 0)

        for player in self.game.players:
            if player.player_number == self.local_player:
                x, y = self.pixel_positions[self.local_player]
                x += math.floor(player.vel[0] * self.pixels_per_frame)
                y += math.floor(player.vel[1] * self.pixels_per_frame)
                new_pos = pygame.Rect(x, y, self.block_size, self.block_size)
                
                collision = new_pos.collidelist(maze_walls)
                if collision != -1:
                    collision = maze_walls[collision]
                    if player.vel[0] == 1:
                        x = collision.x - collision.w
                    elif player.vel[0] == -1:
                        x = collision.x + collision.w
                    elif player.vel[1] == 1:
                        y = collision.y - collision.h
                    elif player.vel[1] == -1:
                        y = collision.y + collision.h
                    else:
                        x, y = self.pixel_positions[self.local_player]
                    new_pos = pygame.Rect(x, y, self.block_size, self.block_size)
                
                pygame.draw.rect(self.screen, RED, new_pos, 0)
                
                self.pixel_positions[self.local_player] = x, y
                new_coords = self.to_coords(new_pos.center)
                
                player.x = new_coords[0]
                player.y = new_coords[1]
                
            else:
                pygame.draw.rect(self.screen, RED, (player.x * self.block_size, player.y * self.block_size, self.block_size, self.block_size), 0)



            """(x, y) =  self.pixel_positions[player.player_number]
            (x0, y0) = self.to_pixels((player.x, player.y))
            if (player.vel == (0, 0) or
                (abs(x0 - x) > self.block_size or abs(y0 - y) > self.block_size)
            ):
                x = x0
                y = y0
            else:
                x += round(player.vel[0] * self.block_size / FRAMES_PER_TICK)
                y += round(player.vel[1] * self.block_size / FRAMES_PER_TICK)
                if not self.legal_move_pixels((x, y)):
                    x = x0
                    y = y0

            self.pixel_positions[player.player_number] = (x, y)
            
        """

    def finish(self):
        winner_text = "Winners: " + str(self.game.winners)
        self.screen.fill(BLACK)
        pygame.font.init()
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render(winner_text, False, WHITE)

        center = (self.res / 2, self.res / 2)

        self.screen.blit(textsurface, center)

    def to_pixels(self, coords):
        return (
            math.floor(coords[0] / self.width * self.res),
            math.floor(coords[1] / self.width * self.res)
        )
    def to_coords(self, pixels):
        return (
            math.floor(pixels[0] / self.res * self.width),
            math.floor(pixels[1] / self.res * self.width)
        )

    def legal_move_pixels(self, pixels):
        return self.game.legal_move(self.to_coords(pixels))
