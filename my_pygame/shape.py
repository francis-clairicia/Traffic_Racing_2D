# -*- coding: Utf-8 -*

import pygame
from .drawable import Drawable
from .colors import TRANSPARENT

class Shape(Drawable):

    TYPE_RECT = 0
    TYPE_CIRCLE = 1

    def __init__(self, shape_type: int, color: pygame.Color, outline=0, outline_color=(0, 0, 0), **kwargs):
        Drawable.__init__(self, **kwargs)
        draw_function = {
            Shape.TYPE_RECT: pygame.draw.rect,
            Shape.TYPE_CIRCLE: pygame.draw.ellipse
        }
        self.__draw_function = draw_function[shape_type]
        self.color = color
        self.outline = outline
        self.outline_color = outline_color

    @property
    def color(self) -> pygame.Color:
        return self.__color

    @color.setter
    def color(self, value: pygame.Color) -> None:
        self.__color = pygame.Color(value) if value is not None else TRANSPARENT

    @property
    def outline(self) -> int:
        return self.__outline

    @outline.setter
    def outline(self, value: int) -> None:
        self.__outline = int(value)
        if self.__outline < 0:
            self.__outline = 0

    @property
    def outline_color(self) -> pygame.Color:
        return self.__outline_color

    @outline_color.setter
    def outline_color(self, value: pygame.Color) -> None:
        self.__outline_color = pygame.Color(value) if value is not None else TRANSPARENT

    def before_drawing(self, surface: pygame.Surface) -> None:
        self.fill(TRANSPARENT)
        self.__draw_function(self.image, self.color, self.image.get_rect())
        self.mask_update()

    def after_drawing(self, surface: pygame.Surface) -> None:
        if self.outline > 0:
            self.__draw_function(surface, self.outline_color, self.rect, self.outline)

class RectangleShape(Shape):

    def __init__(self, width: int, height: int, color: tuple, **kwargs):
        Shape.__init__(self, Shape.TYPE_RECT, color, **kwargs)
        self.set_size(width, height)

class CircleShape(Shape):
    def __init__(self, radius: int, color: tuple, **kwargs):
        Shape.__init__(self, Shape.TYPE_CIRCLE, color, **kwargs)
        self.radius = radius

    @property
    def radius(self) -> int:
        return self.__radius

    @radius.setter
    def radius(self, value: int) -> None:
        self.__radius = int(value)
        if self.__radius < 0:
            self.__radius = 0
        self.set_size(self.__radius * 2)