import pygame
from game import *
black = 0, 0, 0
white = 255, 255, 255
yellow = 255, 255, 0

class Renderer:
    def __init__(self, screen, res, game_state):
        self.screen = screen
        self.res = res
        self.game = game_state
        self.maze = game_state.maze
        self.width = self.game.maze.width
        self.block_size = res / self.width
    
    def render(self):
        self.screen.fill(black)  

        for y in range(self.width):
            for x in range(self.width):
                if self.maze.maze[y * self.width + x]:
                    col = white
                else: col = black
                
                pygame.draw.rect(self.screen, col, (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 0)
        
        pygame.draw.rect(self.screen, yellow, 
            (self.maze.goal[0] * self.block_size, self.maze.goal[1] * self.block_size, self.block_size, self.block_size), 0)
        
        for player in self.game.players:
            pygame.draw.rect(self.screen, (255, 0, 0), (player.x * self.block_size, player.y * self.block_size, self.block_size, self.block_size), 0)
    
    def finish(self):
        winner_text = "Winners: " + str(self.game.winners)
        self.screen.fill(black)
        pygame.font.init()
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render(winner_text, False, white)
        
        center = (self.res / 2, self.res / 2)

        self.screen.blit(textsurface, center)