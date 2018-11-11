from __future__ import division
import os
import math
import pygame

from client_config import FRAME_RATE, BLOCKS_PER_SEC
# max updates to server per second (also move speed in coords)
from config import TICK_RATE

clock = pygame.time.Clock()

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

        self.prio = 'x'

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


                walls = bounding_rect.collidelistall(self.walls)
                if walls:
                    for wall_index in walls:
                        wall = self.walls[wall_index]

                        x_intsec_1 = wall.x + self.block_size - bounding_rect.x
                        x_intsec_2 = wall.x - (bounding_rect.x + self.block_size)
                        y_intsec_1 = wall.y + self.block_size - bounding_rect.y
                        y_intsec_2 = wall.y - (bounding_rect.y + self.block_size)

                        x_intersect = (x_intsec_1 if abs(x_intsec_1) < abs(x_intsec_2)
                            else x_intsec_2)
                        y_intersect = (y_intsec_1 if abs(y_intsec_1) < abs(y_intsec_2)
                            else y_intsec_2)

                        def make_rect(x, y):
                            return pygame.Rect(x, y,
                                               self.block_size,
                                               self.block_size)

                        next_bounding_rect_x = make_rect(
                            bounding_rect.x + x_intersect,
                            bounding_rect.y)
                        next_bounding_rect_y = make_rect(
                            bounding_rect.x,
                            bounding_rect.y + y_intersect)
                        next_bounding_rect_both = make_rect(
                            bounding_rect.x + x_intersect,
                            bounding_rect.y + y_intersect)
                        if (x_intersect < y_intersect and
                            abs(x_intersect) < 1.5 * self.pixels_per_frame
                            and next_bounding_rect_x.collidelist(self.walls) == -1
                        ):
                            self.x = next_bounding_rect_x.x + self.radius

                        elif (y_intersect < x_intersect
                            and abs(y_intersect) < 1.5 * self.pixels_per_frame
                            and next_bounding_rect_y.collidelist(self.walls) == -1
                        ):
                            self.y = next_bounding_rect_y.y + self.radius
                        else:
                            self.x = next_bounding_rect_both.x + self.radius
                            self.y = next_bounding_rect_both.y + self.radius


            new_pos = self.to_coords((self.x, self.y))
            if new_pos[0] != self.player.x and new_pos[1] != self.player.y:
                # can't move in x and y at the same time
                if clock.get_time() > 1000 / TICK_RATE:
                    if self.prio == 'x':
                        self.player.x = new_pos[0]
                        self.prio = 'y'
                    else:
                        self.player.y = new_pos[1]
                        self.prio = 'x'

                    clock.tick()
            elif new_pos != (self.player.x, self.player.y):
                if clock.get_time() > 1000 / TICK_RATE:
                    self.player.x, self.player.y = new_pos
                    clock.tick()
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
