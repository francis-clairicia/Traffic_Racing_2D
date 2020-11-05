# -*- coding: Utf-8 -*

import pygame
from .drawable import Drawable

class Shape(Drawable):

    def __init__(self, surface: pygame.Surface, color: tuple, outline=0, outline_color=(0, 0, 0), **kwargs):
        Drawable.__init__(self, surface=surface, **kwargs)
        self.color = color
        self.outline = outline
        self.outline_color = outline_color

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value: tuple):
        self.__color = tuple(value) if value is not None else (0, 0, 0, 0)

    @property
    def outline(self) -> int:
        return self.__outline

    @outline.setter
    def outline(self, value: int) -> None:
        self.__outline = int(value)
        if self.__outline < 0:
            self.__outline = 0

    @property
    def outline_color(self):
        return self.__outline_color

    @outline_color.setter
    def outline_color(self, value: tuple):
        self.__outline_color = tuple(value) if value is not None else (0, 0, 0, 0)

class RectangleShape(Shape):

    def __init__(self, width: int, height: int, color: tuple, **kwargs):
        Shape.__init__(self, pygame.Surface((int(width), int(height)), flags=pygame.SRCALPHA), color, **kwargs)

    def before_drawing(self, surface: pygame.Surface) -> None:
        self.fill(self.color)

    def after_drawing(self, surface: pygame.Surface) -> None:
        if self.outline > 0:
            pygame.draw.rect(surface, self.outline_color, self.rect, self.outline)

class CircleShape(Shape):
    def __init__(self, radius: int, color: tuple, **kwargs):
        Shape.__init__(self, pygame.Surface((abs(radius) * 2, abs(radius) * 2), flags=pygame.SRCALPHA), color, **kwargs)
        self.radius = radius

    def before_drawing(self, surface: pygame.Surface) -> None:
        new_image = pygame.Surface((self.radius * 2, self.radius * 2), flags=pygame.SRCALPHA)
        new_image.fill((0, 0, 0, 0))
        if self.color:
            pygame.draw.circle(new_image, self.color, (self.radius, self.radius), self.radius)
        self.image = new_image

    def after_drawing(self, surface: pygame.Surface) -> None:
        if self.outline > 0:
            pygame.draw.circle(surface, self.outline_color, self.center, self.radius, self.outline)

    @property
    def radius(self) -> int:
        return self.__radius

    @radius.setter
    def radius(self, value: int) -> None:
        self.__radius = int(value)
        if self.__radius < 0:
            self.__radius = 0