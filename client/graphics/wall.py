import pygame
import os

# globals
DIR = os.path.dirname(os.path.realpath(__file__))

class Wall(pygame.sprite.Sprite):
    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)

        tile = os.path.join(DIR, 'sprites/sprites/wall_mid.png')

        self.image = pygame.transform.scale(pygame.image.load(tile), (rect.w, rect.h))
        self.rect = rect
