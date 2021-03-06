import os
import pygame
import math
from client_config import FRAME_RATE

# globals
SPRITE_UPDATE_INTERVAL = math.floor(FRAME_RATE / 8)

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, images, rect, offsets):
        pygame.sprite.Sprite.__init__(self)
        self.size = (rect[2], rect[3])

        self.image_sets = dict()
        if isinstance(images, dict):
            for key, image_set in images.items():
                self.image_sets[key] = []
                for image in image_set:
                    img = pygame.image.load(image)
                    self.image_sets[key].append(pygame.transform.scale(img, self.size))
        else:
            self.image_sets['default'] = []
            for image in images:
                img = pygame.image.load(image)
                self.image_sets['default'].append(pygame.transform.scale(img, self.size))

        # Take the first element of the dict
        # as the default sprite
        self.current_set_key = next(iter(self.image_sets))
        self.images = self.image_sets[self.current_set_key]
        self.image_number = 0
        self.image_amount = len(self.images)
        self.frames_since_image_update = 1 # when it's 0, update sprite

        self.image = self.images[self.image_number]

        self.x_offset = offsets[0]
        self.y_offset = offsets[1]

        self.x = rect[0]
        self.y = rect[1]
        self.rect = pygame.Rect(round(self.x - self.x_offset), round(self.y - self.y_offset),
                                self.image.get_width(), self.image.get_height())

    def update(self):
        if self.frames_since_image_update == SPRITE_UPDATE_INTERVAL:
            self.next_image()
        else:
            self.frames_since_image_update += 1

    def next_image(self):
        self.image_number = (self.image_number + 1) % self.image_amount
        self.image = self.images[self.image_number]
        self.frames_since_image_update = 0

    def add_image_set(self, key, images):
        self.image_sets[key] = []
        for image in images:
            self.image_sets[key].append(pygame.image.load(image))

    def switch_image_set(self, key):
        self.images = self.image_sets[key]
        self.current_set_key = key
