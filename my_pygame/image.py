# -*- coding: Utf-8 -*

import os
from typing import Sequence
import pygame
from .path import set_constant_file

def set_size(surface, *args) -> pygame.Surface:
    size = args if len(args) == 2 else args[0]
    if not isinstance(size, (tuple, list)):
        size = (size, size)
    size = (round(size[0]), round(size[1]))
    if size[0] > 0 and size[1] > 0:
        surface = pygame.transform.smoothscale(surface, size)
    return surface

def set_width(surface, size, width: float)-> pygame.Surface:
    height = 0 if width == 0 else round(size[1] * width / size[0])
    return set_size(surface, width, height)

def set_height(surface, size, height: float) -> pygame.Surface:
    width = 0 if height == 0 else round(size[0] * height / size[1])
    return set_size(surface, width, height)

def load_image(filepath: str, size=None, width=None, height=None) -> pygame.Surface:
    filepath = set_constant_file(filepath)
    surface = pygame.image.load(filepath).convert_alpha()
    w, h = surface.get_size()
    if size is not None:
        surface = set_size(surface, size)
    elif width is not None and height is not None:
        if w > width:
            surface = set_width(surface, (w, h), width)
        if h > height:
            surface = set_height(surface, (w, h), height)
    elif width is not None:
        surface = set_width(surface, (w, h), width)
    elif height is not None:
        surface = set_height(surface, (w, h), height)
    return surface

def load_image_list(filepath_list: Sequence[str], size=None, width=None, height=None) -> Sequence[pygame.Surface]:
    return tuple(load_image(filepath, size, width, height) for filepath in filepath_list)