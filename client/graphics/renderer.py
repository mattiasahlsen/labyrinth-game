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
        self.pixelPositions = []

    def render_connect_screen(self):
        self.screen.fill(BACKGROUND)
        self.input_box.update()
        self.input_box.draw(self.screen)

    def init_game(self, game_state):
        self.game = game_state
        self.maze = self.game.maze
        self.width = self.maze.width
        self.block_size = self.res / self.width
        self.pixelPositions = [None] * len(game_state.players)

        for player in game_state.players:
            self.pixelPositions[player.player_number] = self.toPixels((player.x, player.y))

    def render_game(self):
        self.screen.fill(BLACK)

        for y in range(self.width):
            for x in range(self.width):
                if self.maze.maze[y * self.width + x]:
                    col = WHITE
                else: col = BLACK

                pygame.draw.rect(self.screen, col, (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 0)

        pygame.draw.rect(self.screen, YELLOW,
                        (self.maze.goal[0] * self.block_size, self.maze.goal[1] * self.block_size, self.block_size, self.block_size), 0)

        for player in self.game.players:
            (x, y) =  self.pixelPositions[player.player_number]
            (x0, y0) = self.toPixels((player.x, player.y))
            x += round((x0 - x) / FRAMES_PER_TICK)
            y += round((y0 - y) / FRAMES_PER_TICK)
            self.pixelPositions[player.player_number] = (x, y)
            pygame.draw.rect(self.screen, RED, (x, y, self.block_size, self.block_size), 0)

    def finish(self):
        winner_text = "Winners: " + str(self.game.winners)
        self.screen.fill(BLACK)
        pygame.font.init()
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render(winner_text, False, WHITE)

        center = (self.res / 2, self.res / 2)

        self.screen.blit(textsurface, center)

    def toPixels(self, coords):
        return (
            math.floor(coords[0] / self.width * self.res),
            math.floor(coords[1] / self.width * self.res)
        )
