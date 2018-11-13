import math
import pygame
from os import path
from graphics.colors import *
from .sprite import Sprite
from .wall import Wall

from config import GAME_WIDTH
from client_config import FRAME_RATE, BLOCKS_PER_SEC, VIEW_DISTANCE

DIR = path.dirname(path.realpath(__file__))

class Renderer:
    def __init__(self, screen, res, game):
        self.screen = screen
        screen.fill(BLACK)
        self.res = res

        self.game = game
        self.maze = self.game.maze
        self.width = self.maze.width

        self.block_size = math.floor(self.res / VIEW_DISTANCE)

        self.sprites = pygame.sprite.RenderPlain()
        walls_rect = []
        for y in range(self.width):
            for x in range(self.width):
                if self.maze.maze[y * self.width + x]:
                    self.sprites.add(
                        Wall((x * self.block_size, y * self.block_size), self.block_size)
                    )
                    walls_rect.append(
                         pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                    )

        # goal sprite
        (goal_x, goal_y) = self.to_pixels((self.maze.goal[0], self.maze.goal[1]))
        self.goal = pygame.sprite.Sprite()
        self.goal.image = pygame.image.load(path.join(DIR, 'sprites/sprites/coin_anim_f0.png'))
        self.goal.image = pygame.transform.scale(self.goal.image, (self.block_size, self.block_size))

        self.goal.rect = pygame.Rect(goal_x, goal_y, self.block_size, self.block_size)
        self.sprites.add(self.goal)

        self.background = pygame.Surface((self.width * self.block_size,
                                          self.width * self.block_size))
        self.background.fill(BLACK)
        self.sprites.draw(self.background)

        self.player_sprites = pygame.sprite.Group()
        for player in game.players:
            sprite = Sprite(game, player, self.block_size, walls_rect)
            self.player_sprites.add(sprite)
            if player.local:
                self.local_player = sprite

    def render_game(self):
        self.player_sprites.update()

        x = min(max(0, math.floor(self.local_player.x - self.res / 2)), self.width * self.block_size - self.res)
        y = min(max(0, math.floor(self.local_player.y - self.res / 2)), self.width * self.block_size - self.res)
        sub_background = self.background.subsurface(pygame.Rect(x, y, self.res, self.res))

        self.screen.blit(sub_background, (0, 0))
        self.player_sprites.draw(self.screen)

    def update_res(self, res):
        return Renderer(self.screen, res, self.game)

    def finish(self):
        winner_amount = len(self.game.winners)
        if winner_amount > 1:
            winner_text = "Draw! The winners are: "

            for i in range(winner_amount):
                winner_text += self.game.players[self.game.winners[i]].name
                if not i == winner_amount - 1:
                    winner_text += ', '
        else:
            winner_text = self.game.players[self.game.winners[0]].name + " wins!"

        font = pygame.font.SysFont(None, int(self.block_size * 8))
        textsurface = font.render(winner_text, False, ORANGE)
        text_rect = textsurface.get_rect()

        text_pos = self.res // 2 - text_rect.w // 2, self.res // 2 - text_rect.h // 2

        self.screen.blit(textsurface, text_pos)

    def to_pixels(self, coords):
        return (
            math.floor(coords[0] * self.block_size),
            math.floor(coords[1] * self.block_size)
        )
    def to_coords(self, pixels):
        return (
            math.floor(pixels[0] * self.block_size),
            math.floor(pixels[1] * self.block_size)
        )
