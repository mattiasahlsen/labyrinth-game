import os
from .animated_sprite import AnimatedSprite

DIR = os.path.dirname(os.path.realpath(__file__))

class CoinSprite(AnimatedSprite):
    def __init__(self, rect):
        get_image = lambda n: os.path.join(DIR, 'sprites/sprites/coin_anim_f' + str(n) + '.png')
        images = []
        for i in range(4):
            images.append(get_image(i))

        AnimatedSprite.__init__(self, images, rect, (0, 0))
        