import os.path
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, player_number, location):
        self.player_number = player_number
        self.x = location[0]
        self.y = location[1]
        self.vel = (0, 0)


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
        return dict([('player_number', self.player_number), ('x', self.x), ('y', self.y)])

class LocalPlayer(Player):
    pass
