import os
import pygame
from graphics.colors import BOX_INACTIVE, BOX_ACTIVE

FONT_SIZE = 18
DIR = os.path.dirname(os.path.realpath(__file__))

class InputBox:
    def __init__(self, x, y, w, text):
        self.rect = pygame.Rect(x, y, w, FONT_SIZE + 5)
        self.color = BOX_INACTIVE
        self.desc = text + ': '
        self.text = ''
        self.font = pygame.font.Font(DIR + '/res/fonts/Montserrat-Regular.ttf', FONT_SIZE)
        self.text_surface = self.font.render('', True, self.color)
        self.desc_surface = self.font.render(self.desc, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = BOX_ACTIVE if self.active else BOX_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.text_surface = self.font.render(self.text, True, self.color)
        return None

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.text_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the description
        screen.blit(self.desc_surface, (self.rect.x - self.desc_surface.get_width() - 5, self.rect.y))
        # Blit the text.
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 1)
