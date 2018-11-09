import pygame
from graphics.colors import *

class Renderer:
    def __init__(self, screen, res, input_box):
        self.screen = screen
        self.res = res
        self.input_box = input_box
        self.block_size = None
        self.game = None
        self.maze = None
        self.width = None

    def render_connect_screen(self):
        self.screen.fill(BACKGROUND)
        self.input_box.update()
        self.input_box.draw(self.screen)

    def init_game(self, game_state):
        self.game = game_state
        self.maze = self.game.maze
        self.width = self.maze.width
        self.block_size = self.res / self.width

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
            pygame.draw.rect(self.screen, RED, (player.x * self.block_size, player.y * self.block_size, self.block_size, self.block_size), 0)

    def finish(self):
        winner_text = "Winners: " + str(self.game.winners)
        self.screen.fill(BLACK)
        pygame.font.init()
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render(winner_text, False, WHITE)

        center = (self.res / 2, self.res / 2)

        self.screen.blit(textsurface, center)
