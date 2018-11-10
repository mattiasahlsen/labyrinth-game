import math
import pygame
from graphics.colors import *
from sprite import Sprite

from config import GAME_WIDTH, TICK_RATE
from client_config import FRAME_RATE, WINDOW_WIDTH, BLOCKS_PER_SEC

# globals
FRAMES_PER_TICK = FRAME_RATE / TICK_RATE # float

class Renderer:
    def __init__(self, screen, res, game):
        self.screen = screen
        self.res = res

        self.game = None
        self.maze = None
        self.width = None
        self.pixel_positions = []

        self.game = game
        self.maze = self.game.maze
        self.width = self.maze.width

        self.block_size = self.res / self.width
        self.pixels_per_frame =  self.block_size * BLOCKS_PER_SEC / FRAME_RATE


        # draw walls only once
        self.walls = []
        for y in range(self.width):
            for x in range(self.width):
                if self.maze.maze[y * self.width + x]:
                    self.walls.append(
                       pygame.draw.rect(self.screen, WHITE, (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 0)
                    )

        self.sprites = pygame.sprite.Group()
        for player in game.players:
            self.sprites.add(Sprite(game, player, self.block_size, self.walls))

    """
    def render_walls(self):
        self.screen.fill(BLACK)
        for wall in self.walls:
            pygame.draw.rect(self.screen, WHITE, wall, 0)

        pygame.draw.rect(self.screen, YELLOW,
                        (self.maze.goal[0] * self.block_size, self.maze.goal[1] * self.block_size, self.block_size, self.block_size), 0)
    """

    def render_game(self):
        self.sprites.update()
        self.sprites.clear(self.screen, BLACK)
        self.sprites.draw(self.screen)

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
