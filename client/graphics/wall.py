import pygame
import os

# globals
DIR = os.path.dirname(os.path.realpath(__file__))

class Wall(pygame.sprite.Sprite):
    def __init__(self, pixel_coords, size):
        pygame.sprite.Sprite.__init__(self)
        self.pixel_coords = pixel_coords
        self.size = size

        tile = os.path.join(DIR, 'sprites/sprites/wall_mid.png')

        self.image = pygame.image.load(tile)
        self.image = pygame.transform.scale(self.image, (size, size))
        
        #self.image = pygame.Surface((size, size))
        #self.image.fill((128,128,128))

        self.rect = pixel_coords[0], pixel_coords[1], size, size
        