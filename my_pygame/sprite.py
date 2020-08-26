# -*- coding: Utf-8 -*

from typing import Sequence
import pygame
from .classes import Drawable
from .clock import Clock

class Sprite(Drawable):

    __slots__ = (
        "__sprites",
        "__sprite_idx",
        "__clock",
        "__wait_time",
        "__animation",
        "__loop"
    )

    def __init__(self, *img_list: Sequence[pygame.Surface], **kwargs):
        self.__sprites = img_list
        Drawable.__init__(self, self.__sprites[0], **kwargs)
        self.__sprite_idx = 0
        self.__clock = Clock()
        self.__wait_time = 0
        self.__animation = False
        self.__loop = False

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
            self.__sprite_idx += 1
            self.__sprite_idx %= len(self.__sprites)
            self.image = self.__sprites[self.__sprite_idx]
            if self.__sprite_idx == 0 and not self.__loop:
                self.__animation = False

    def draw(self, surface: pygame.Surface) -> None:
        self.__update_animation()
        Drawable.draw(self, surface)

    def start_animation(self, loop=False):
        self.__animation = True
        self.__loop = bool(loop)

    def stop_animation(self, reset=True):
        self.__animation = self.__loop = False
        if reset:
            self.__sprite_idx = 0
            self.image = self.__sprites[0]