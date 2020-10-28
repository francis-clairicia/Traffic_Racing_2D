# -*- coding: Utf-8 -*

from typing import Sequence, Union
import pygame
from .classes import Image
from .clock import Clock

class Sprite(Image):

    def __init__(self, *img: pygame.Surface, **kwargs):
        self.__sprites = img
        Image.__init__(self, self.__sprites[0], **kwargs)
        self.__nb_sprites = len(self.__sprites)
        self.__sprite_idx = 0
        self.__clock = Clock()
        self.__wait_time = 0
        self.__animation = False
        self.__loop = False
        self.__fix_width = bool("width" in kwargs)
        self.__fix_height = bool("height" in kwargs)

    @classmethod
    def from_list(cls, img_list: Sequence[pygame.Surface], **kwargs):
        return cls(*img_list, **kwargs)

    @property
    def ratio(self):
        return self.__wait_time

    @ratio.setter
    def ratio(self, value):
        self.__wait_time = float(value)

    def animated(self):
        return self.__animation

    def __update_animation(self):
        if self.__animation and self.__clock.elapsed_time(self.__wait_time):
            self.__sprite_idx = (self.__sprite_idx + 1) % self.__nb_sprites
            self.load(self.__sprites[self.__sprite_idx], keep_width=self.__fix_width, keep_height= self.__fix_height)
            if self.__sprite_idx == 0 and not self.__loop:
                self.__animation = False

    def before_drawing(self, surface: pygame.Surface) -> None:
        self.__update_animation()

    def start_animation(self, loop=False):
        self.__animation = True
        self.__loop = bool(loop)

    def stop_animation(self, reset=True):
        self.__animation = self.__loop = False
        if reset:
            self.__sprite_idx = 0
            self.image = self.__sprites[0]