import os.path
import pygame
from .character import Character

class Player(Character):
    def __init__(self, player_number, location, name):
        self.id = player_number
        self.x = location[0]
        self.y = location[1]
        self.local = False
        self.name = name

class LocalPlayer(Player):
    def __init__(self, number, location, name):
        Player.__init__(self, number, location, name)
        self.vel = (0, 0)
        self.local = True
        self.illegal_move = False
