# -*- coding: Utf-8 -*

import os
import pygame
from typing import Tuple, Union, Dict, List, Any, Iterator
from .thread import threaded_function

def find_in_iterable(iterable, *key_before, valid_callback=None) -> Iterator[Tuple[Union[int, str], ...]]:
    if isinstance(iterable, dict):
        for key, value in iterable.items():
            yield from find_in_iterable(value, *key_before, key, valid_callback=valid_callback)
    elif isinstance(iterable, (list, tuple)):
        for index, value in enumerate(iterable):
            yield from find_in_iterable(value, *key_before, index, valid_callback=valid_callback)
    else:
        value = iterable
        if not callable(valid_callback) or valid_callback(value):
            yield key_before

def travel_container(key_path: Tuple[Union[int, str], ...], container: Dict[str, Any]) -> Tuple[Union[int, str], Union[List[str], Dict[Any, str]]]:
    for i in range(len(key_path) - 1):
        container = container[key_path[i]]
    return key_path[-1], container

def find_value_in_container(key_path: Tuple[Union[int, str], ...], container: Dict[str, Any]) -> Any:
    try:
        key, container = travel_container(key_path, container)
        value = container[key]
    except (IndexError, KeyError):
        return None
    return value

class Resources:

    __slots__ = ("__img", "__font", "__music", "__sfx", "__loaded")

    def __init__(self):
        self.__img = dict()
        self.__font = dict()
        self.__music = dict()
        self.__sfx = dict()
        self.__loaded = 0

    @property
    def loaded(self) -> int:
        return self.__loaded

    @property
    def img_to_load(self) -> Iterator[Tuple[Union[int, str], ...]]:
        return find_in_iterable(self.__img, valid_callback=os.path.isfile)

    @property
    def font_to_load(self) -> Iterator[Tuple[Union[int, str], ...]]:
        return find_in_iterable(self.__font, valid_callback=lambda path: not os.path.isfile(path))

    @property
    def music_to_load(self) -> Iterator[Tuple[Union[int, str], ...]]:
        return find_in_iterable(self.__music, valid_callback=lambda path: not os.path.isfile(path))

    @property
    def sfx_to_load(self) -> Iterator[Tuple[Union[int, str], ...]]:
        return find_in_iterable(self.__sfx, valid_callback=os.path.isfile)

    def __len__(self) -> int:
        return sum(len(list(iterator)) for iterator in [self.img_to_load, self.font_to_load, self.music_to_load, self.sfx_to_load])

    def load(self) -> None:
        if self.__loaded:
            return
        loading_method = [
            (self.__img, self.img_to_load, lambda resource: pygame.image.load(resource).convert_alpha()),
            (self.__font, self.font_to_load, lambda resource: None),
            (self.__music, self.music_to_load, lambda resource: None),
            (self.__sfx, self.sfx_to_load, lambda resource: pygame.mixer.Sound(resource))
        ]
        for resources_container, resources_finder, resources_loader in loading_method:
            for key_path in resources_finder:
                key, container = travel_container(key_path, resources_container)
                container[key] = resources_loader(container[key])
                self.__loaded += 1

    @threaded_function
    def threaded_load(self) -> None:
        self.load()

    def set_sfx_volume(self, volume: float, state: bool) -> float:
        if volume < 0:
            volume = 0
        elif volume > 1:
            volume = 1
        for key_path in find_in_iterable(self.__sfx, valid_callback=lambda obj: isinstance(obj, pygame.mixer.Sound)):
            sound_obj = self.get_sfx(*key_path)
            sound_obj.set_volume(volume if bool(state) is True else 0)
        return volume

    def play_sfx(self, *key_path) -> (pygame.mixer.Channel, None):
        sound = self.get_sfx(*key_path)
        if sound is None:
            return None
        return sound.play()

    def get_img(self, *key_path) -> pygame.Surface:
        return find_value_in_container(key_path, self.__img)

    def get_font(self, *key_path) -> str:
        return find_value_in_container(key_path, self.__font)

    def get_music(self, *key_path) -> str:
        return find_value_in_container(key_path, self.__music)

    def get_sfx(self, *key_path) -> pygame.mixer.Sound:
        return find_value_in_container(key_path, self.__sfx)

    def __add_to_dict(self, resource_dict: dict, resources: dict) -> None:
        if not self.__loaded and isinstance(resources, dict):
            resource_dict.update(resources)

    IMG = property(lambda self: self.__img, lambda self, value: self.__add_to_dict(self.__img, value))
    FONT = property(lambda self: self.__font, lambda self, value: self.__add_to_dict(self.__font, value))
    MUSIC = property(lambda self: self.__music, lambda self, value: self.__add_to_dict(self.__music, value))
    SFX = property(lambda self: self.__sfx, lambda self, value: self.__add_to_dict(self.__sfx, value))

RESOURCES = Resources()