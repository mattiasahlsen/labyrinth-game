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

        self.images = []
        for image in images:
            self.images.append(pygame.image.load(image))
        self.image_number = 0
        self.image_amount = len(self.images)

        self.frames_since_image_update = 1 # when it's 0, update sprite

        for i in range(len(self.images)):
            self.images[i] = pygame.transform.scale(self.images[i], self.size)

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
