import os.path
import math
import pygame
from random import randint
from game.avatars import AVATARS

id_ = 0

def random_avatar():
    return AVATARS[randint(0, len(AVATARS) - 1)]

class Player(pygame.sprite.Sprite):
    def __init__(self, location, name, avatar=None, mId = None):
        if mId:
            self.id = mId
        else:
            global id_
            self.id = id_
            id_ += 1

        self.x = location[0]
        self.y = location[1]
        self.vel = (0, 0)

        self.local = False
        self.name = name
        if avatar:
            self.avatar = avatar
        else:
            self.avatar = random_avatar()

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

    def serializable_init(self):
        return { **self.serializable(),
                 **dict([('name', self.name), ('avatar', self.avatar)]) }

class LocalPlayer(Player):
    def __init__(self, location, name, avatar=None):
        Player.__init__(self, location, name, avatar)
        self.local = True
        self.illegal_move = False
