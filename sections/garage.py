# -*- coding: Utf-8 -*

import pygame
from my_pygame import Window, ImageButton, Image
from my_pygame import GRAY, YELLOW
from constants import IMG, AUDIO
from save import SAVE

class Garage(Window):

    def __init__(self):
        Window.__init__(self, bg_color=GRAY, bg_music=AUDIO["garage"])
        params_for_all_buttons = {
            "highlight_color": YELLOW,
            "hover_sound": AUDIO["select"],
        }
        self.button_back = ImageButton(self, Image(IMG["blue_arrow"]), **params_for_all_buttons, command=self.stop)
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())
        self.bind_joystick_button(0, "B", lambda event: self.stop())

    def place_objects(self):
        self.button_back.topleft = (5, 5)

    def on_quit(self):
        self.play_sound(AUDIO["back"])