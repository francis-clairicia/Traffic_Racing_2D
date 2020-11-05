# -*- coding: Utf-8 -*

import pygame
from .drawable import Drawable

class Image(Drawable):

    def __init__(self, surface: pygame.Surface, size=None, width=None, height=None, **kwargs):
        Drawable.__init__(self, surface=surface, size=size, width=width, height=height, **kwargs)

    @classmethod
    def from_filepath(cls, filepath: str, **kwargs):
        return cls(surface=pygame.image.load(filepath).convert_alpha(), **kwargs)

    def load(self, surface: pygame.Surface, **kwargs):
        self.image = self.resize_surface(surface, **kwargs)