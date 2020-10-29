# -*- coding: Utf-8 -*

import math
from typing import Tuple

class Vector:

    __slots__ = ("__x", "__y")

    def __init__(self, x: float, y: float):
        self.__x = self.__y = 0
        self.x = x
        self.y = y

    @classmethod
    def from_two_points(cls, point_1: Tuple[float, float], point_2: Tuple[float, float]):
        return cls(point_2[0] - point_1[0], point_2[1] - point_1[1])

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value: float):
        self.__x = float(value)

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value: float):
        self.__x = float(value)

    def norm(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))

    def cross_product(self, vector):
        return (self.x * vector.y) - (self.y * vector.x)

    def dot_product(self, vector):
        return (self.x * vector.x) + (self.y * vector.y)

    def angle_with_vector(self, vector):
        try:
            angle = math.acos(self.dot_product(vector) / (self.norm() * vector.norm()))
        except ZeroDivisionError:
            angle = 0
        return angle