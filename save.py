# -*- coding: Utf-8 -*

import sys
import os
import pickle
import pygame

class Save:
    def __init__(self):
        self.__save_file = os.path.join(sys.path[0], "files", "save.bin")
        if os.path.isfile(self.__save_file):
            with open(self.__save_file, "rb") as save:
                self.__save = pickle.load(save)
        else:
            self.__save = dict()
            self.set_default_options()
            self.reset()
    
    def __getitem__(self, key: str):
        return self.__save[key]
    
    def __setitem__(self, key: str, value):
        self.__save[key] = value
    
    def dump(self):
        with open(self.__save_file, "wb") as save:
            pickle.dump(self.__save, save)

    def set_default_options(self):
        self.__save["fps"] = False
        self.__save["auto_acceleration"] = False
        self.__save["controls"] = {
            "speed_up": {"key": "RIGHT", "joy": "A"},
            "brake": {"key": "LEFT", "joy": "B"},
            "up": {"key": "UP", "joy": "UP"},
            "down": {"key": "DOWN", "joy": "DOWN"}
        }

    def reset(self):
        self.__save["highscore"] = 0
        self.__save["money"] = 0
        self.__save["car"] = 1
        self.__save["owned_cars"] = {
            1:True,
            2:False,
            3:False,
            4:False,
            5:False,
            6:False,
            7:False,
            8:False,
            9:False
        }

SAVE = Save()