# -*- coding: Utf-8 -*

from typing import Tuple
import pygame.math

class Vector2(pygame.math.Vector2):

    @classmethod
    def from_two_points(cls, point_1: Tuple[float, float], point_2: Tuple[float, float]):
        return cls(point_2[0] - point_1[0], point_2[1] - point_1[1])
