import math
import pygame
from os import path
from random import randint
from graphics.colors import *
from .player_sprite import PlayerSprite
from .coin_sprite import CoinSprite
from .wall import Wall
from .floor_sprite import FloorSprite

from config import GAME_WIDTH
from client_config import FRAME_RATE, BLOCKS_PER_SEC, VIEW_DISTANCE

DIR = path.dirname(path.realpath(__file__))
AVATARS = ['elf_m', 'elf_f', 'knight_m', 'knight_f', 'wizzard_m', 'wizzard_f']
def random_avatar():
    return AVATARS[randint(0, len(AVATARS) - 1)]


class Renderer:
    def __init__(self, screen, res, game):
        self.screen = screen
        screen.fill(BLACK)
        self.res = res

        self.game = game
        self.maze = self.game.maze
        self.width = self.maze.width

        self.block_size = math.floor(self.res / VIEW_DISTANCE)

        self.walls = pygame.sprite.RenderPlain()
        self.floors = pygame.sprite.RenderPlain()
        self.sprites = pygame.sprite.Group()
        for y in range(self.width):
            for x in range(self.width):
                rect = pygame.Rect(x * self.block_size, y * self.block_size,
                                    self.block_size, self.block_size)
                if self.maze.maze[y * self.width + x]:
                    self.walls.add(Wall(rect))
                else:
                    self.floors.add(FloorSprite(rect))

        # goal sprite
        (goal_x, goal_y) = self.to_pixels(self.maze.goal[0], self.maze.goal[1])
        goal = CoinSprite((goal_x, goal_y, self.block_size, self.block_size))
        self.sprites.add(goal)

        self.background = pygame.Surface((self.width * self.block_size,
                                          self.width * self.block_size))
        self.background.fill(BLACK)
        self.floors.draw(self.background)
        self.walls.draw(self.background)

        for player in game.players:
            sprite = PlayerSprite(player, self.block_size, random_avatar())
            self.sprites.add(sprite)
            if player.local:
                self.local_player = player

    def render_game(self):
        x = round(max(0, min(math.floor(self.local_player.px - self.res / 2), self.width * self.block_size - self.res)))
        y = round(max(0, min(math.floor(self.local_player.py - self.res / 2), self.width * self.block_size - self.res)))

        sub_background = self.background.subsurface(pygame.Rect(x, y, self.res, self.res))
        self.sprites.update(x, y)

        self.screen.blit(sub_background, (0, 0))
        self.sprites.draw(self.screen)

    def update_res(self, res, game):
        return Renderer(self.screen, res, game)

    def finish(self):
        self.screen.fill((1, 1, 1), None, pygame.BLEND_RGBA_SUB)

        winner_amount = len(self.game.winners)
        if winner_amount > 1:
            winner_text = "Draw! The winners are: "

            for i in range(winner_amount):
                winner_text += self.game.players[self.game.winners[i]].name
                if not i == winner_amount - 1:
                    winner_text += ', '
        else:
            winner_text = self.game.players[self.game.winners[0]].name + " wins!"

        font = pygame.font.Font(DIR + '/res/fonts/Montserrat-Regular.ttf', int(self.block_size) * 4)
        textsurface = font.render(winner_text, True, WIN_SCREEN_TEXT)
        textsurface = pygame.transform.scale(textsurface, (self.res // 2, int(textsurface.get_height() * self.res / (2 * textsurface.get_width()))))

        font = pygame.font.Font(DIR + '/res/fonts/Montserrat-Regular.ttf', int(textsurface.get_height() * self.res / (2 * textsurface.get_width())))
        textsurface = font.render(winner_text, True, WIN_SCREEN_TEXT)
        text_rect = textsurface.get_rect()

        text_pos = self.res // 2 - text_rect.w // 2, self.res // 2 - text_rect.h // 2

        self.screen.blit(textsurface, text_pos)

    def to_pixels(self, x, y):
        return (
            math.floor(x * self.block_size),
            math.floor(y * self.block_size)
        )
