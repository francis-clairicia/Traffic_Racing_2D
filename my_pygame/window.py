# -*- coding: Utf-8 -*

import os
import sys
import configparser
from typing import Callable, Any, Union, Optional, Type, Sequence
import pygame
from .abstract import Drawable, Focusable
from .classes import Text, RectangleShape
from .list import DrawableList
from .joystick import Joystick
from .keyboard import Keyboard
from .clock import Clock
from .path import set_constant_file
from .resources import RESOURCES

CONFIG_FILE = set_constant_file("window.conf")

class WindowCallback(object):
    def __init__(self, callback: Callable[..., Any], wait_time: float):
        self.wait_time = wait_time
        self.callback = callback
        self.clock = Clock()

    def can_call(self) -> bool:
        return self.clock.elapsed_time(self.wait_time, restart=False)

    def __call__(self):
        return self.callback()

class Window:

    surface = property(lambda self: pygame.display.get_surface())
    __all_opened = list()
    __sound_volume = 0
    __music_volume = 0
    __enable_music = True
    __enable_sound = True
    actual_music = None
    __show_fps = False
    __fps = 60
    __fps_obj = None
    __joystick = list()
    keyboard = Keyboard()

    def __init__(self, master=None, size=(0, 0), flags=0, bg_color=(0, 0, 0), bg_music=None):
        Window.init_pygame(size, flags)
        self.__master = master
        self.rect = self.surface.get_rect()
        self.main_clock = pygame.time.Clock()
        self.loop = False
        self.objects = DrawableList()
        self.event_handler_dict = dict()
        self.key_handler_dict = dict()
        self.key_state_dict = dict()
        self.joystick_handler_dict = dict()
        self.mouse_handler_list = list()
        self.bg_color = bg_color
        self.callback_after = list()
        self.rect_to_update = None
        self.bg_music = bg_music
        focus_event = (
            pygame.KEYDOWN,
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
            pygame.MOUSEWHEEL,
            pygame.JOYHATMOTION
        )
        for event in focus_event:
            self.bind_event(event, self.handle_focus)
        mouse_hide_event = (
            pygame.KEYDOWN,
            pygame.KEYUP,
            pygame.JOYBUTTONDOWN,
            pygame.JOYBUTTONUP,
            pygame.JOYAXISMOTION,
            pygame.JOYHATMOTION
        )
        mouse_show_event = (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
            pygame.MOUSEWHEEL,
        )
        for event_list, status in zip((mouse_show_event, mouse_hide_event), (True, False)):
            for event in event_list:
                self.bind_event(event, lambda event, state=status: pygame.mouse.set_visible(state))
        self.__key_enabled = True
        self.__screenshot = False
        self.bind_key(pygame.K_F11, lambda event: self.screenshot())
        if not Window.__fps_obj:
            Window.__fps_obj = Text(color=(0, 0, 255))

    @staticmethod
    def init_pygame(size=(0, 0), flags=0):
        if not pygame.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 512)
            status = pygame.init()
            if status[1] > 0:
                print("Error on pygame initialization ({} modules failed to load)".format(status[1]), file=sys.stderr)
                sys.exit(84)
            Window.load_config()
        if pygame.display.get_surface() is None:
            if size[0] <= 0 or size[1] <= 0:
                video_info = pygame.display.Info()
                size = video_info.current_w, video_info.current_h
            pygame.display.set_mode(tuple(size), flags)
            RESOURCES.load()
            RESOURCES.set_sfx_volume(Window.__sound_volume, Window.__enable_sound)

    @property
    def main_window(self) -> bool:
        if not Window.__all_opened:
            return True
        return bool(Window.__all_opened[0] == self)

    def set_joystick(self, nb_joysticks: int):
        Window.__joystick = [Joystick(i) for i in range(nb_joysticks)]
        for joy in self.joystick:
            self.bind_event(pygame.JOYDEVICEADDED, joy.event_connect)
            self.bind_event(pygame.CONTROLLERDEVICEADDED, joy.event_connect)
            self.bind_event(pygame.JOYDEVICEREMOVED, joy.event_disconnect)
            self.bind_event(pygame.CONTROLLERDEVICEREMOVED, joy.event_disconnect)

    @property
    def joystick(self) -> Sequence[Joystick]:
        return Window.__joystick

    def joy_search_device_index_from_instance_id(self, instance_id: int):
        for i, joy in enumerate(self.joystick):
            if joy.id == instance_id:
                return i
        return -1

    def __setattr__(self, name, obj):
        if isinstance(obj, (Drawable, DrawableList)) and name != "objects":
            self.objects.add(obj)
        return object.__setattr__(self, name, obj)

    def __delattr__(self, name):
        if isinstance(obj, (Drawable, DrawableList)) and name != "objects":
            self.objects.remove(obj)
        return object.__delattr__(self, name)

    def __contains__(self, obj):
        return bool(obj in self.objects)

    def enable_key_joy_focus(self):
        self.__key_enabled = True

    def disable_key_joy_focus(self):
        self.__key_enabled = False

    @staticmethod
    def set_icon(icon: pygame.Surface):
        pygame.display.set_icon(icon)

    @staticmethod
    def set_title(title: str):
        pygame.display.set_caption(title)

    @property
    def bg_music(self):
        return self.__bg_music

    @bg_music.setter
    def bg_music(self, music):
        if music is None or os.path.isfile(music):
            self.__bg_music = music

    def mainloop(self):
        self.loop = True
        Window.__all_opened.append(self)
        self.place_objects()
        self.set_grid()
        if Focusable.MODE != Focusable.MODE_MOUSE and self.objects.focus_get() is None:
            self.objects.focus_next()
        while self.loop:
            for callback in [c for c in self.callback_after if c.can_call()]:
                callback()
                self.callback_after.remove(callback)
            self.fps_update()
            self.update()
            self.keyboard.update()
            self.draw_and_refresh()
            self.event_handler()
            self.handle_bg_music()

    def stop(self, force=False, sound=None):
        self.loop = False
        self.on_quit()
        if sound:
            self.play_sound(sound)
        if self.main_window or force is True:
            Window.save_config()
            pygame.quit()
            sys.exit(0)
        Window.__all_opened.remove(self)

    def on_quit(self):
        pass

    def update(self):
        pass

    def place_objects(self):
        pass

    def set_grid(self):
        pass

    def draw_screen(self, show_fps=True):
        if self.bg_color:
            self.surface.fill(self.bg_color)
        if isinstance(self.__master, Window):
            self.__master.draw_screen(show_fps=False)
        self.objects.draw(self.surface)
        if Window.__show_fps is True and show_fps:
            Window.__fps_obj.draw(self.surface)
        if self.__screenshot:
            pygame.draw.rect(self.surface, (255, 255, 255), self.rect, width=30)

    @staticmethod
    def set_fps(framerate: int) -> None:
        Window.__fps = int(framerate)

    @staticmethod
    def show_fps(status: bool):
        Window.__show_fps = bool(status)

    @staticmethod
    def config_fps_obj(**kwargs):
        Window.__fps_obj.config(**kwargs)

    @staticmethod
    def move_fps_object(**kwargs):
        Window.__fps_obj.move(**kwargs)

    @staticmethod
    def fps_is_shown() -> bool:
        return Window.__show_fps

    def fps_update(self):
        self.main_clock.tick(Window.__fps)
        if Window.__show_fps:
            Window.__fps_obj.message = f"{round(self.main_clock.get_fps())} FPS"

    def show_all(self, without=tuple()):
        for obj in self.objects:
            if obj not in without:
                obj.show()

    def hide_all(self, without=tuple()):
        for obj in self.objects:
            if obj not in without:
                obj.hide()

    def refresh(self):
        pygame.display.update(self.rect_to_update if self.rect_to_update else self.rect)

    def draw_and_refresh(self, *args, **kwargs):
        self.draw_screen(*args, **kwargs)
        self.refresh()

    def event_handler(self):
        for key_value, callback_list in self.key_state_dict.items():
            for callback in callback_list:
                callback(key_value, self.keyboard.is_pressed(key_value))
        for callback in self.mouse_handler_list:
            callback(pygame.mouse.get_pos())
        for joy_id in self.joystick_handler_dict:
            if joy_id not in range(len(self.joystick)):
                continue
            for id_, callback_list in self.joystick_handler_dict[joy_id].items():
                if id_.startswith("AXIS"):
                    for callback in callback_list:
                        callback(self.joystick[joy_id].get_value(id_))
        for event in pygame.event.get():
            if event.type == pygame.QUIT \
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_F4 and (event.mod & pygame.KMOD_LALT)):
                self.stop(force=True)
            elif event.type == pygame.KEYDOWN:
                for callback in self.key_handler_dict.get(event.key, tuple()):
                    callback(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                joy = self.joy_search_device_index_from_instance_id(event.instance_id)
                for callback in self.joystick_handler_dict.get(joy, dict()).get(self.joystick[joy].search_key("button", event.button), tuple()):
                    callback(event)
            for callback in self.event_handler_dict.get(event.type, tuple()):
                callback(event)

    def set_focus(self, obj: Drawable) -> None:
        self.objects.set_focus(obj)

    def handle_focus(self, event: pygame.event.Event) -> None:
        if event.type in [pygame.KEYDOWN, pygame.JOYHATMOTION]:
            Focusable.MODE = Focusable.MODE_KEY if event.type == pygame.KEYDOWN else Focusable.MODE_JOY
            if self.__key_enabled:
                side_with_key_event = {
                    pygame.K_LEFT: Focusable.ON_LEFT,
                    pygame.K_RIGHT: Focusable.ON_RIGHT,
                    pygame.K_UP: Focusable.ON_TOP,
                    pygame.K_DOWN: Focusable.ON_BOTTOM,
                }
                side_with_joystick_hat_event = {
                    (-1, 0): Focusable.ON_LEFT,
                    (1, 0): Focusable.ON_RIGHT,
                    (0, 1): Focusable.ON_TOP,
                    (0, -1): Focusable.ON_BOTTOM,
                }
                if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    self.objects.focus_next()
                else:
                    key_events = [
                        (pygame.KEYDOWN, "key", side_with_key_event),
                        (pygame.JOYHATMOTION, "value", side_with_joystick_hat_event)
                    ]
                    for event_type, attr, side_dict in key_events:
                        if event.type != event_type:
                            continue
                        value = getattr(event, attr)
                        if value in side_dict:
                            self.objects.focus_obj_on_side(side_dict[value])
        else:
            Focusable.MODE = Focusable.MODE_MOUSE

    def after(self, milliseconds: float, callback: Callable[..., Any]):
        self.callback_after.append(WindowCallback(callback, milliseconds))

    def bind_event(self, event_type, callback):
        event_list = self.event_handler_dict.get(event_type)
        if event_list is None:
            event_list = self.event_handler_dict[event_type] = list()
        event_list.append(callback)

    def unbind_event(self, event_type, callback):
        if event_type in self.event_handler_dict and callback in self.event_handler_dict[event_type]:
            self.event_handler_dict[event_type].remove(callback)
            if not self.event_handler_dict[event_type]:
                self.event_handler_dict.pop(event_type)

    def bind_mouse(self, callback):
        self.mouse_handler_list.append(callback)

    def unbind_mouse(self, callback):
        if callback in self.mouse_handler_list:
            self.mouse_handler_list.remove(callback)

    def bind_key(self, key_value, callback, hold=False):
        if not hold:
            key_dict = self.key_handler_dict
        else:
            key_dict = self.key_state_dict
        key_list = key_dict.get(key_value)
        if key_list is None:
            key_list = key_dict[key_value] = list()
        key_list.append(callback)

    def unbind_key(self, key_value, callback):
        if key_value in self.key_handler_dict and callback in self.key_handler_dict[key_value]:
            self.key_handler_dict[key_value].remove(callback)
            if not self.key_handler_dict[key_value]:
                self.key_handler_dict.pop(key_value)
        elif key_value in self.key_state_dict and callback in self.key_state_dict[key_value]:
            self.key_state_dict[key_value].remove(callback)
            if not self.key_state_dict[key_value]:
                self.key_state_dict.pop(key_value)

    def bind_joystick(self, joy_id, action, callback):
        joystick_dict = self.joystick_handler_dict.get(joy_id)
        if joystick_dict is None:
            joystick_dict = self.joystick_handler_dict[joy_id] = dict()
        joystick_list = joystick_dict.get(action)
        if joystick_list is None:
            joystick_list = joystick_dict[action] = list()
        joystick_list.append(callback)

    def screenshot(self):
        if not self.__screenshot:
            self.__screenshot = True
            i = 1
            while os.path.isfile(os.path.join(sys.path[0], f"screenshot_{i}.png")):
                i += 1
            pygame.image.save(self.surface, os.path.join(sys.path[0], f"screenshot_{i}.png"))
            self.after(1000, self.__hide_screenshot_frame)

    def __hide_screenshot_frame(self):
        self.__screenshot = False

    def handle_bg_music(self):
        if not Window.__enable_music or (self.bg_music is None and pygame.mixer.get_busy()):
            self.stop_music()
        elif Window.__enable_music and self.bg_music and (not pygame.mixer.music.get_busy() or Window.actual_music is None or Window.actual_music != self.bg_music):
            self.play_music(self.bg_music)

    @staticmethod
    def stop_music():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        Window.actual_music = None

    @staticmethod
    def play_music(filepath: str):
        Window.stop_music()
        if Window.__enable_music:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(Window.__music_volume)
            pygame.mixer.music.play(-1)
            Window.actual_music = filepath

    @staticmethod
    def play_sound(sound: pygame.mixer.Sound):
        if Window.__enable_sound and isinstance(sound, pygame.mixer.Sound):
            sound.play()

    @staticmethod
    def sound_volume():
        return Window.__sound_volume

    @staticmethod
    def music_volume():
        return Window.__music_volume

    @staticmethod
    def set_sound_volume(value: float):
        Window.__sound_volume = RESOURCES.set_sfx_volume(value, Window.__enable_sound)

    @staticmethod
    def set_music_volume(value: float):
        Window.__music_volume = value
        if Window.__music_volume > 1:
            Window.__music_volume = 1
        elif Window.__music_volume < 0:
            Window.__music_volume = 0
        pygame.mixer.music.set_volume(Window.__music_volume)

    @staticmethod
    def set_music_state(state: bool):
        Window.__enable_music = bool(state)

    @staticmethod
    def set_sound_state(state: bool):
        Window.__enable_sound = bool(state)
        RESOURCES.set_sfx_volume(Window.__sound_volume, Window.__enable_sound)

    @staticmethod
    def get_music_state() -> bool:
        return Window.__enable_music

    @staticmethod
    def get_sound_state() -> bool:
        return Window.__enable_sound

    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        params = {
            "MUSIC": {
                "volume": {
                    "callback": Window.set_music_volume,
                    "get": config.getfloat,
                    "default": 50,
                    "transform": lambda x: x / 100
                },
                "enable": {
                    "callback": Window.set_music_state,
                    "get": config.getboolean,
                    "default": True
                }
            },
            "SFX": {
                "volume": {
                    "callback": Window.set_sound_volume,
                    "get": config.getfloat,
                    "default": 50,
                    "transform": lambda x: x / 100
                },
                "enable": {
                    "callback": Window.set_sound_state,
                    "get": config.getboolean,
                    "default": True
                }
            },
            "FPS": {
                "show": {
                    "callback": Window.show_fps,
                    "get": config.getboolean,
                    "default": False
                }
            },
        }
        for section, option_dict in params.items():
            for option, setup in option_dict.items():
                callback = setup["callback"]
                get_value = setup["get"]
                get_value_params = dict()
                if "default" in setup:
                    get_value_params["fallback"] = setup["default"]
                transform = setup.get("transform", lambda value: value)
                callback(transform(get_value(section, option, **get_value_params)))

    @staticmethod
    def save_config():
        config_dict = {
            "MUSIC": {
                "volume": round(Window.__music_volume * 100),
                "enable": Window.get_music_state()
            },
            "SFX": {
                "volume": round(Window.__sound_volume * 100),
                "enable": Window.get_sound_state()
            },
            "FPS": {
                "show": Window.fps_is_shown()
            }
        }
        config = configparser.ConfigParser()
        config.read_dict(config_dict)
        with open(CONFIG_FILE, "w") as file:
            config.write(file, space_around_delimiters=False)

    left = property(lambda self: self.rect.left)
    right = property(lambda self: self.rect.right)
    top = property(lambda self: self.rect.top)
    bottom = property(lambda self: self.rect.bottom)
    x = left
    y = top
    size = property(lambda self: self.rect.size)
    width = property(lambda self: self.rect.width)
    height = property(lambda self: self.rect.height)
    w = width
    h = height
    center = property(lambda self: self.rect.center)
    centerx = property(lambda self: self.rect.centerx)
    centery = property(lambda self: self.rect.centery)
    topleft = property(lambda self: self.rect.topleft)
    topright = property(lambda self: self.rect.topright)
    bottomleft = property(lambda self: self.rect.bottomleft)
    bottomright = property(lambda self: self.rect.bottomright)
    midtop = property(lambda self: self.rect.midtop)
    midbottom = property(lambda self: self.rect.midbottom)
    midleft = property(lambda self: self.rect.midleft)
    midright = property(lambda self: self.rect.midright)