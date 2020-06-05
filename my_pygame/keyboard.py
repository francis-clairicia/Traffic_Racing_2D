# -*- coding: Utf-8 -*

from typing import Union
import pygame

class Keyboard:

    def __init__(self):
        self.__states = list()

    def update(self):
        self.__states.clear()
        self.__states.extend(pygame.key.get_pressed())

    @property
    def key_dict(self) -> dict:
        return { # Ceci est la liste des keys
            pygame.K_0:     "0",
            pygame.K_1:     "1",
            pygame.K_2:     "2",
            pygame.K_3:     "3",
            pygame.K_4:     "4",
            pygame.K_5:     "5",
            pygame.K_6:     "6",
            pygame.K_7:     "7",
            pygame.K_8:     "8",
            pygame.K_9:     "9",
            pygame.K_a:     "A",
            pygame.K_b:     "B",
            pygame.K_c:     "C",
            pygame.K_d:     "D",
            pygame.K_e:     "E",
            pygame.K_f:     "F",
            pygame.K_g:     "G",
            pygame.K_h:     "H",
            pygame.K_i:     "I",
            pygame.K_j:     "J",
            pygame.K_k:     "K",
            pygame.K_l:     "L",
            pygame.K_m:     "M",
            pygame.K_n:     "N",
            pygame.K_o:     "O",
            pygame.K_p:     "P",
            pygame.K_q:     "Q",
            pygame.K_r:     "R",
            pygame.K_s:     "S",
            pygame.K_t:     "T",
            pygame.K_u:     "U",
            pygame.K_v:     "V",
            pygame.K_w:     "W",
            pygame.K_x:     "X",
            pygame.K_y:     "Y",
            pygame.K_z:     "Z",
            pygame.K_KP0:   "KP 0",
            pygame.K_KP1:   "KP 1",
            pygame.K_KP2:   "KP 2",
            pygame.K_KP3:   "KP 3",
            pygame.K_KP4:   "KP 4",
            pygame.K_KP5:   "KP 5",
            pygame.K_KP6:   "KP 6",
            pygame.K_KP7:   "KP 7",
            pygame.K_KP8:   "KP 8",
            pygame.K_KP9:   "KP 9",
            pygame.K_UP:    "UP",
            pygame.K_DOWN:  "DOWN",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_LEFT:  "LEFT",
        }

    @property
    def key_values(self) -> dict:
        return {v: k for k, v in self.key_dict.items()}

    def __contains__(self, key: int) -> bool:
        return bool(key in self.key_dict)

    def __getitem__(self, key: Union[int, str]) -> Union[int, str, None]:
        if key in self.key_dict:
            return self.key_dict.get(key)
        elif key in self.key_values:
            return self.key_values.get(key)
        return None

    def is_pressed(self, key: Union[int, str]) -> bool:
        try:
            if key in self.key_dict:
                return bool(self.__states[key])
            elif key in self.key_values:
                return bool(self.__states[self.key_values[key]])
        except IndexError:
            pass
        return False