# -*- coding: Utf-8 -*

import os
import pygame
from typing import Tuple, Union, Dict, List, Any

def find_in_iterable(iterable, *key_before, valid_callback=None):
    if isinstance(iterable, dict):
        for key, value in iterable.items():
            yield from find_in_iterable(value, *key_before, key, valid_callback=valid_callback)
    elif isinstance(iterable, (list, tuple)):
        for index, value in enumerate(iterable):
            yield from find_in_iterable(value, *key_before, index, valid_callback=valid_callback)
    else:
        value = iterable
        if valid_callback is None or valid_callback(value):
            yield key_before

def travel_container(key_path: Tuple[Union[int, str], ...], container: Dict[str, Any]) -> Tuple[Union[int, str], Union[List[str], Dict[Any, str]]]:
    for i in range(len(key_path) - 1):
        container = container[key_path[i]]
    return key_path[-1], container

def find_value_in_container(key_path: Tuple[Union[int, str], ...], container: Dict[str, Any]) -> Any:
    key, container = travel_container(key_path, container)
    return container[key]

class Resources:

    __slots__ = ("__img", "__font", "__music", "__sfx")

    def __init__(self):
        self.__img = dict()
        self.__font = dict()
        self.__music = dict()
        self.__sfx = dict()

    def load(self):
        for key_path in find_in_iterable(self.__img, valid_callback=os.path.isfile):
            key, container = travel_container(key_path, self.__img)
            container[key] = pygame.image.load(container[key]).convert_alpha()
        for key_path in find_in_iterable(self.__sfx, valid_callback=os.path.isfile):
            key, container = travel_container(key_path, self.__sfx)
            container[key] = pygame.mixer.Sound(container[key])

    def set_sfx_volume(self, volume: float, state: bool) -> float:
        if volume < 0:
            volume = 0
        elif volume > 1:
            volume = 1
        for key_path in find_in_iterable(self.__sfx, valid_callback=lambda obj: isinstance(obj, pygame.mixer.Sound)):
            sound_obj = find_value_in_container(key_path, self.__sfx)
            sound_obj.set_volume(volume if bool(state) is True else 0)
        return volume

    IMG = property(lambda self: self.__img, lambda self, value: self.__img.update(value if isinstance(value, dict) else dict()))
    FONT = property(lambda self: self.__font, lambda self, value: self.__font.update(value if isinstance(value, dict) else dict()))
    MUSIC = property(lambda self: self.__music, lambda self, value: self.__music.update(value if isinstance(value, dict) else dict()))
    SFX = property(lambda self: self.__sfx, lambda self, value: self.__sfx.update(value if isinstance(value, dict) else dict()))

RESOURCES = Resources()