import pygame
import os
from random import randint

# globals
DIR = os.path.dirname(os.path.realpath(__file__))

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

class FloorSprite(pygame.sprite.Sprite):
    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)

        # 80x80
        sheet = pygame.image.load(os.path.join(DIR, 'sprites/sprites/floor_tilesheet.png'))

        x = 16 * randint(1, 3)
        y = 16 * randint(1, 3)
        tile = sheet.subsurface(x, y, 16, 16)


        self.image = pygame.transform.scale(tile, (rect.w, rect.h))
        self.rect = rect
