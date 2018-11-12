import os.path
import pygame


class Character(pygame.sprite.Sprite):
    def __init__(self,id, location, name):
        self.id = id
        self.x = location[0]
        self.y = location[1]
        self.local = False
        self.name = name

    def move(self):
        self.x += self.vel[0]
        self.y += self.vel[1]

    def move_to(self, destination):
        self.x = destination[0]
        self.y = destination[1]

    def current_pos(self):
        return (self.x, self.y)

    def next_pos(self):
        return (self.x + self.vel[0], self.y + self.vel[1])

    def serializable(self):
        return dict([('id', self.id), ('x', self.x), ('y', self.y)])

