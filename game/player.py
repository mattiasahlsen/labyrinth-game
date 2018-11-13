import os.path
import math
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, number, location, name):
        self.id = number
        self.x = location[0]
        self.y = location[1]
        self.vel = (0, 0)

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

class LocalPlayer(Player):
    def __init__(self, number, location, name):
        Player.__init__(self, number, location, name)
        self.local = True
        self.illegal_move = False
