from __future__ import division
import os
import math
import pygame

from client_config import FRAME_RATE, BLOCKS_PER_SEC
from config import TICK_RATE # updates from server per second


# globals
DIR = os.path.dirname(os.path.realpath(__file__))
FRAMES_PER_TICK = FRAME_RATE / TICK_RATE # float
SPRITE_UPDATE_INTERVAL = math.floor(FRAME_RATE / 8)

class Sprite(pygame.sprite.Sprite):
    def __init__(self, game, player, block_size, walls):
        pygame.sprite.Sprite.__init__(self)

        # should be a float
        self.pixels_per_frame =  block_size * BLOCKS_PER_SEC / FRAME_RATE

        self.game = game
        self.maze = self.game.maze
        self.player = player
        self.block_size = block_size
        self.walls = walls

        get_image = lambda n: os.path.join(DIR, 'sprites/sprites/elf_f_run_anim_f' + str(n) + '.png')
        self.images = []
        for n in range(0, 4):
            self.images.append(pygame.image.load(get_image(n)))
        self.image_number = 0
        self.image = self.images[self.image_number]
        self.update_sprite = 1 # when it's 0, update sprite

        self.img_width = self.image.get_width()
        self.img_height = self.image.get_height()
        self.x_offset = self.img_width / 2
        self.y_offset = self.img_width * 1.2 # to look better

        self.radius = self.block_size / 2 # pixels to center
        self.x = player.x * block_size + self.radius # pixel position
        self.y = player.y * block_size + self.radius
        self.rect = pygame.Rect(round(self.x - self.x_offset), round(self.y - self.y_offset),
                                self.img_width, self.img_height)

    def update(self):
        if self.update_sprite == 0:
            self.image_number = (self.image_number + 1) % 4
            self.image = self.images[self.image_number]
        self.update_sprite = (self.update_sprite + 1) % SPRITE_UPDATE_INTERVAL

        if self.player.local:
            if self.player.illegal_move:
                self.player.illegal_move = False
                (self.x, self.y) = self.to_pixels((self.player.x, self.player.y))
                (self.x, self.y) = (self.x + self.radius, self.y + self.radius)

            else:
                self.x += self.pixels_per_frame * self.player.vel[0]
                self.y += self.pixels_per_frame * self.player.vel[1]

                maze_pixel_width = self.maze.width * self.block_size
                if self.x - self.radius < 0:
                    self.x = self.radius
                elif self.x + self.radius > maze_pixel_width:
                    self.x = maze_pixel_width - self.radius
                if self.y - self.radius < 0:
                    self.y = self.radius
                elif self.y + self.radius > maze_pixel_width:
                    self.y = maze_pixel_width - self.radius


                bounding_rect = pygame.Rect(round(self.x - self.radius),
                                            round(self.y - self.radius),
                                            self.block_size, self.block_size)


                wall = bounding_rect.collidelist(self.walls)
                if not wall == -1:
                    wall = self.walls[wall]
                    x_intersect = min(wall.x + self.block_size - bounding_rect.x,
                                      bounding_rect.x + self.block_size - wall.x)
                    y_intersect = min(wall.y + self.block_size - bounding_rect.y,
                                      bounding_rect.y + self.block_size - wall.y)

                    if x_intersect < y_intersect:
                        if self.x % self.block_size > self.radius:
                            self.x = math.floor(wall.x - self.radius)
                        else:
                            self.x = math.ceil(wall.x + wall.w + self.radius)
                    else:
                        if self.y % self.block_size > self.radius:
                            self.y = math.floor(wall.y - self.radius)
                        else:
                            self.y = math.ceil(wall.y + wall.h + self.radius)


            self.player.x, self.player.y = self.to_coords((self.x, self.y))
        else:
            (realX, realY) = self.to_pixels((self.player.x, self.player.y))
            self.x = (realX - self.x) / FRAMES_PER_TICK
            self.y = (realY - self.y) / FRAMES_PER_TICK

        self.rect[0], self.rect[1] = (round(self.x - self.x_offset),
                                      round(self.y - self.y_offset))

    def to_pixels(self, coords):
        return (
            math.floor(coords[0] * self.block_size),
            math.floor(coords[1] * self.block_size)
        )

    def to_coords(self, pixels):
        return (
            math.floor(pixels[0] / self.block_size),
            math.floor(pixels[1] / self.block_size)
        )
