# -*-coding:Utf-8-*

import os
import sys
from typing import Tuple, Union, Optional
import pickle
import pygame

class Joystick(object):

    def __init__(self, index: int):
        self.__index = index
        self.__joystick = None

        self.__button_list = ["A", "B", "X", "Y", "L1", "L2", "R1", "R2", "SELECT", "START", "L3", "R3", "HOME"]
        self.__axis_list = ["AXIS_LEFT_X", "AXIS_LEFT_Y", "AXIS_RIGHT_X", "AXIS_RIGHT_Y"]
        self.__dpad_list = ["UP", "DOWN", "LEFT", "RIGHT"]

        self.__event_type = {key: [str(), -1, 0] for key in self.button_list + self.axis_list + self.dpad_list}
        self.__event_state = {key: dict() for key in ("button", "axis", "hat")}

        self.__save_file = os.path.join(sys.path[0], "joystick.bin")
        if os.path.isfile(self.__save_file):
            with open(self.__save_file, "rb") as save:
                self.__save = pickle.load(save)
        else:
            self.__save = dict()
            self.set_default_layout()
        self.__nb_update = 0
        self.__nb_update_to_uninitialize = 60
        self.__button_axis_return_bool = True

    """-----------------------------------------------------"""

    def connected(self) -> bool:
        return bool(self.__joystick is not None)

    def event_connect(self, event: pygame.event.Event) -> None:
        if self.connected():
            return
        if event.type in (pygame.CONTROLLERDEVICEADDED, pygame.JOYDEVICEADDED) and event.device_index == self.__index:
            self.__joystick = pygame.joystick.Joystick(event.device_index)
            self.__joystick.init()

    def event_disconnect(self, event: pygame.event.Event) -> None:
        if not self.connected():
            return
        if event.type in (pygame.CONTROLLERDEVICEREMOVED, pygame.JOYDEVICEREMOVED) and event.instance_id == self.id:
            self.__joystick.quit()
            self.__joystick = None

    def update(self) -> None:
        if not self.connected():
            return
        joystick = self.__joystick
        try:
            if self.guid in self.__save:
                self.__event_type = self.__save[self.guid]
            else:
                self.set_default_layout()
            actions = [
                ("button", joystick.get_numbuttons, joystick.get_button),
                ("axis", joystick.get_numaxes, joystick.get_axis),
                ("hat", joystick.get_numhats, joystick.get_hat),
            ]
            for event, get_max_number, get_value in actions:
                for i in range(get_max_number()):
                    self.__event_state[event][i] = get_value(i)
        except pygame.error:
            for key in self.__event_state:
                self.__event_state[key].clear()

    """------------------------------------------------------------------"""

    def set_default_layout(self):
        layout = {
            "A":            ("button", 0, 1),
            "B":            ("button", 1, 1),
            "X":            ("button", 2, 1),
            "Y":            ("button", 3, 1),
            "L1":           ("button", 4, 1),
            "R1":           ("button", 5, 1),
            "SELECT":       ("button", 6, 1),
            "START":        ("button", 7, 1),
            "L3":           ("button", 8, 1),
            "R3":           ("button", 9, 1),
            "HOME":         ("button", 10, 1),
            "UP":           ("hat", 0, (0, 1)),
            "DOWN":         ("hat", 0, (0, -1)),
            "LEFT":         ("hat", 0, (-1, 0)),
            "RIGHT":        ("hat", 0, (1, 0)),
            "L2":           ("axis", 2, 0),
            "R2":           ("axis", 5, 0),
            "AXIS_LEFT_X":  ("axis", 0, 0),
            "AXIS_LEFT_Y":  ("axis", 1, 0),
            "AXIS_RIGHT_X": ("axis", 3, 0),
            "AXIS_RIGHT_Y": ("axis", 4, 0),
        }
        for key in layout:
            for i in range(3):
                self.__event_type[key][i] = layout[key][i]

    def __save_to_file(self):
        self.__save[self.guid] = dict(self.__event_type)
        with open(self.__save_file, "wb") as save:
            pickle.dump(self.__save, save)

    """------------------------------------------------------------------"""

    @property
    def button_list(self):
        return self.__button_list

    @property
    def axis_list(self):
        return self.__axis_list

    @property
    def dpad_list(self):
        return self.__dpad_list

    """------------------------------------------------------------------"""

    def __test(self, key: str) -> None:
        key = key.upper()
        if key not in self.button_list + self.axis_list + self.dpad_list:
            raise NameError("{} isn't recognized".format(key))
        return key

    def __get_event_type(self, key: str) -> Tuple[str, str, int, int]:
        key = self.__test(key)
        infos = self.__event_type[key]
        return (key, *infos)

    def get_value(self, key: str) -> int:
        key = self.__test(key)
        infos = self.__event_type[key]
        return infos[1]

    def search_key(self, event_type: str, index: int, hat_value: Optional[Tuple[int, int]] = (0, 0)) -> Union[str, None]:
        for key, value in self.__event_type.items():
            event, idx, value = value
            if event == event_type and idx == index and (event != "hat" or value == hat_value):
                return key
        return None

    def __getitem__(self, key: str) -> Union[int, float]:
        key, event, index, active_state = self.__get_event_type(key)
        if event not in self.__event_state:
            return 0
        state = self.__event_state[event].get(index, 0)
        if key in self.button_list + self.dpad_list:
            if event == "button":
                return state
            if event == "hat" and isinstance(state, tuple):
                return 1 if all(active_state[i] == 0 or state[i] == active_state[i] for i in range(2)) else 0
            if event == "axis":
                if self.__button_axis_return_bool:
                    return 1 if state >= 0.9 else 0
                return state
            return 0
        return state

    def set_event(self, key: str, event: int, index: int, hat_value: Optional[Tuple[int, int]] = (0, 0)) -> None:
        key = self.__test(key)
        event_map = {
            pygame.JOYBUTTONDOWN: ("button", index, 1),
            pygame.JOYAXISMOTION: ("axis", index, 0),
            pygame.JOYHATMOTION: ("hat", index, hat_value)
        }
        if event in event_map:
            for i in range(len(event_map[event])):
                self.__event_type[key][i] = event_map[event][i]
            self.__save_to_file()

    def set_button_axis(self, state: bool) -> None:
        self.__button_axis_return_bool = bool(state)

    """------------------------------------------------------------------"""

    @property
    def id(self) -> int:
        return self.__joystick.get_instance_id() if self.connected() else -1

    @property
    def guid(self) -> str:
        return self.__joystick.get_guid() if self.connected() else str()

    @property
    def name(self) -> str:
        return self.__joystick.get_name() if self.connected() else str()

    """------------------------------------------------------------------"""

    @staticmethod
    def count() -> int:
        return len(Joystick.list())

    @staticmethod
    def list() -> Tuple[str, ...]:
        return tuple(joystick.get_name() for joystick in [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())])

    """------------------------------------------------------------------"""

    A = property(lambda self: self.get_value("A"))
    B = property(lambda self: self.get_value("B"))
    X = property(lambda self: self.get_value("X"))
    Y = property(lambda self: self.get_value("Y"))
    L1 = property(lambda self: self.get_value("L1"))
    L2 = property(lambda self: self.get_value("L2"))
    L3 = property(lambda self: self.get_value("L3"))
    R1 = property(lambda self: self.get_value("R1"))
    R2 = property(lambda self: self.get_value("R2"))
    R3 = property(lambda self: self.get_value("R3"))
    SELECT = property(lambda self: self.get_value("SELECT"))
    START = property(lambda self: self.get_value("START"))
    UP = property(lambda self: self.get_value("UP"))
    DOWN = property(lambda self: self.get_value("DOWN"))
    LEFT = property(lambda self: self.get_value("LEFT"))
    RIGHT = property(lambda self: self.get_value("RIGHT"))
    AXIS_LEFT_X = property(lambda self: self.get_value("AXIS_LEFT_X"))
    AXIS_LEFT_Y = property(lambda self: self.get_value("AXIS_LEFT_Y"))
    AXIS_RIGHT_X = property(lambda self: self.get_value("AXIS_RIGHT_X"))
    AXIS_RIGHT_Y = property(lambda self: self.get_value("AXIS_RIGHT_Y"))