import pygame
import os
from random import randint

# globals
DIR = os.path.dirname(os.path.realpath(__file__))

class FloorSprite(pygame.sprite.Sprite):
    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)

        tile = os.path.join(DIR, 'sprites/sprites/floor_' + random_sprite() + '.png')

        self.image = pygame.transform.scale(pygame.image.load(tile), (rect.w, rect.h))
        self.rect = rect

def random_sprite():
    n = 0
    r = randint(0, 100)
    if r < 75:
        n = 1
    elif r < 80:
        n = 5
    else:
        n = randint(1, 8)
    return str(n)
