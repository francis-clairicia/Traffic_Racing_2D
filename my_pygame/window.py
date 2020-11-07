# -*- coding: Utf-8 -*

import os
import sys
import configparser
from typing import Callable, Any, Union, Optional, Type, Sequence, Tuple
import pygame
from .drawable import Drawable
from .focusable import Focusable
from .text import Text
from .shape import RectangleShape
from .progress import ProgressBar
from .list import DrawableList
from .joystick import Joystick, JoystickList
from .keyboard import Keyboard
from .clock import Clock
from .colors import BLACK, WHITE, BLUE, TRANSPARENT
from .resources import RESOURCES
from .multiplayer import ServerSocket, ClientSocket

CONFIG_FILE = os.path.join(sys.path[0], "window.conf")

class WindowCallback(object):
    def __init__(self, callback: Callable[..., Any], wait_time: float):
        self.wait_time = wait_time
        self.callback = callback
        self.clock = Clock()

    def can_call(self) -> bool:
        return self.clock.elapsed_time(self.wait_time, restart=False)

    def __call__(self):
        return self.callback()

class Window(object):

    MIXER_FREQUENCY = 44100
    MIXER_SIZE = -16
    MIXER_CHANNELS = 2
    MIXER_BUFFER = 512

    __main_window = None
    __default_key_repeat = (0, 0)
    __text_input_enabled = False
    __all_opened = list()
    __sound_volume = 0
    __music_volume = 0
    __enable_music = True
    __enable_sound = True
    __actual_music = None
    __show_fps = False
    __fps = 60
    __fps_obj = None
    __joystick = JoystickList()
    __all_window_event_handler_dict = dict()
    __keyboard = Keyboard()
    __all_window_key_enabled = True
    __server_socket = ServerSocket()
    __client_socket = ClientSocket()

    def __init__(self, master=None, size=(0, 0), flags=0, bg_color=BLACK, bg_music=None, loading=None):
        if not isinstance(Window.__main_window, Window):
            Window.__main_window = self
        self.__init_pygame(size, flags, loading)
        self.__master = master
        self.__main_clock = pygame.time.Clock()
        self.__loop = False
        self.__show_fps_in_this_window = True
        self.objects = DrawableList()
        self.__event_handler_dict = dict()
        self.__key_handler_dict = dict()
        self.__key_state_dict = dict()
        self.__joystick_handler_dict = dict()
        self.__joystick_state_dict = dict()
        self.__mouse_handler_list = list()
        self.__callback_after = list()
        self.rect_to_update = None
        self.bg_color = bg_color
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
        self.__key_enabled = True
        self.__screenshot = False
        self.bind_key(pygame.K_F11, lambda event: self.screenshot())
        if not Window.__fps_obj:
            Window.__fps_obj = Text(color=BLUE)

    def __init_pygame(self, size: Tuple[int, int], flags: int, loading) -> None:
        if not pygame.get_init():
            pygame.mixer.pre_init(Window.MIXER_FREQUENCY, Window.MIXER_SIZE, Window.MIXER_CHANNELS, Window.MIXER_BUFFER)
            status = pygame.init()
            if status[1] > 0:
                print("Error on pygame initialization ({} modules failed to load)".format(status[1]), file=sys.stderr)
                sys.exit(1)
            Window.load_config()
            Window.bind_event_all_window(pygame.JOYDEVICEADDED, Window.__joystick.event_connect)
            Window.bind_event_all_window(pygame.CONTROLLERDEVICEADDED, Window.__joystick.event_connect)
            Window.bind_event_all_window(pygame.JOYDEVICEREMOVED, Window.__joystick.event_disconnect)
            Window.bind_event_all_window(pygame.CONTROLLERDEVICEREMOVED, Window.__joystick.event_disconnect)
        if pygame.display.get_surface() is None:
            if size[0] <= 0 or size[1] <= 0:
                video_info = pygame.display.Info()
                size = video_info.current_w, video_info.current_h
            pygame.display.set_mode(tuple(size), flags)
            self.__load_resources(loading)

    def __load_resources(self, loading) -> None:
        nb_resources_to_load = len(RESOURCES)
        if nb_resources_to_load == 0:
            return
        if loading is None or not issubclass(loading, Window):
            RESOURCES.load()
        else:
            loading().mainloop()
        RESOURCES.set_sfx_volume(Window.__sound_volume, Window.__enable_sound)

    @property
    def main_window(self) -> bool:
        return bool(Window.__main_window == self)

    @property
    def joystick(self) -> JoystickList:
        return Window.__joystick

    @property
    def keyboard(self) -> Keyboard:
        return Window.__keyboard

    def __setattr__(self, name, obj) -> None:
        if isinstance(obj, (Drawable, DrawableList)) and name != "objects":
            self.objects.add(obj)
        return object.__setattr__(self, name, obj)

    def __delattr__(self, name) -> None:
        if isinstance(obj, (Drawable, DrawableList)) and name != "objects":
            self.objects.remove(obj)
        return object.__delattr__(self, name)

    def __contains__(self, obj) -> bool:
        return bool(obj in self.objects)

    def enable_key_joy_focus(self) -> None:
        self.__key_enabled = True

    def disable_key_joy_focus(self) -> None:
        self.__key_enabled = False

    @staticmethod
    def enable_key_joy_focus_for_all_window() -> None:
        Window.__all_window_key_enabled = True

    @staticmethod
    def disable_key_joy_focus_for_all_window() -> None:
        Window.__all_window_key_enabled = False

    @staticmethod
    def set_icon(icon: pygame.Surface) -> None:
        pygame.display.set_icon(pygame.transform.smoothscale(icon, (32, 32)))

    @staticmethod
    def set_title(title: str) -> None:
        pygame.display.set_caption(title)

    @property
    def bg_music(self) -> Union[str, None]:
        return self.__bg_music

    @bg_music.setter
    def bg_music(self, music) -> None:
        if music is None or os.path.isfile(music):
            self.__bg_music = music

    @property
    def bg_color(self) -> pygame.Color:
        return self.__bg_color

    @bg_color.setter
    def bg_color(self, color: pygame.Color) -> None:
        self.__bg_color = pygame.Color(color) if color is not None else TRANSPARENT

    @property
    def loop(self) -> bool:
        return self.__loop

    def mainloop(self) -> None:
        self.__loop = True
        Window.__all_opened.append(self)
        self.place_objects()
        self.set_grid()
        self.fps_update()
        self.on_start_loop()
        while self.__loop:
            for callback in filter(lambda window_callback: window_callback.can_call(), self.__callback_after.copy()):
                callback()
                self.__callback_after.remove(callback)
            self.__main_clock.tick(Window.__fps)
            self.objects.focus_mode_update()
            self.keyboard.update()
            self.update()
            self.draw_and_refresh()
            self.event_handler()
            self.handle_bg_music()

    def stop(self, force=False, sound=None) -> None:
        self.__loop = False
        self.on_quit()
        self.set_focus(None)
        if sound:
            self.play_sound(sound)
        if self.main_window or force is True:
            for window in filter(lambda win: win != self, Window.__all_opened):
                window.on_quit()
            Window.stop_connection()
            Window.save_config()
            pygame.quit()
            sys.exit(0)
        Window.__all_opened.remove(self)

    def on_quit(self) -> None:
        pass

    def on_start_loop(self) -> None:
        pass

    def update(self) -> None:
        pass

    def place_objects(self) -> None:
        pass

    def set_grid(self) -> None:
        pass

    def draw_screen(self, show_fps=True) -> None:
        self.surface.fill(self.bg_color)
        if isinstance(self.__master, Window):
            self.__master.draw_screen(show_fps=False)
        self.objects.draw(self.surface)
        if Window.__show_fps is True and show_fps and self.__show_fps_in_this_window:
            Window.__fps_obj.draw(self.surface)
        if self.__screenshot:
            pygame.draw.rect(self.surface, WHITE, self.rect, width=30)

    @staticmethod
    def set_fps(framerate: int) -> None:
        Window.__fps = int(framerate)

    @staticmethod
    def show_fps(status: bool) -> None:
        Window.__show_fps = bool(status)

    @staticmethod
    def config_fps_obj(**kwargs) -> None:
        Window.__fps_obj.config(**kwargs)

    @staticmethod
    def move_fps_object(**kwargs) -> None:
        Window.__fps_obj.move(**kwargs)

    @staticmethod
    def fps_is_shown() -> bool:
        return Window.__show_fps

    def fps_update(self) -> None:
        if Window.__show_fps:
            Window.__fps_obj.message = f"{round(self.__main_clock.get_fps())} FPS"
        self.after(500, self.fps_update)

    def show_fps_in_this_window(self, status: bool) -> None:
        self.__show_fps_in_this_window = bool(status)

    def show_all(self, without=list()) -> None:
        for obj in self.objects:
            if obj not in without:
                obj.show()

    def hide_all(self, without=list()) -> None:
        for obj in self.objects:
            if obj not in without:
                obj.hide()

    def refresh(self) -> None:
        pygame.display.update(self.rect_to_update or self.rect)

    def draw_and_refresh(self, *args, **kwargs) -> None:
        self.draw_screen(*args, **kwargs)
        self.refresh()

    def event_handler(self) -> None:
        for key_value, callback_list in self.__key_state_dict.items():
            for callback in callback_list:
                callback(key_value, self.keyboard.is_pressed(key_value))
        for callback in self.__mouse_handler_list:
            callback(pygame.mouse.get_pos())
        for device_index in self.__joystick_state_dict:
            if self.joystick[device_index] is None:
                continue
            for action, callback_list in self.__joystick_state_dict[device_index].items():
                for callback in callback_list:
                    callback(self.joystick[device_index].get_value(action))
        for event in pygame.event.get():
            if event.type == pygame.QUIT \
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_F4 and (event.mod & pygame.KMOD_LALT)):
                self.stop(force=True)
            elif event.type == pygame.KEYDOWN:
                for callback in self.__key_handler_dict.get(event.key, tuple()):
                    callback(event)
            elif event.type in [pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYHATMOTION]:
                joystick = self.joystick.get_joy_by_instance_id(event.instance_id)
                joystick_handler_dict = self.__joystick_handler_dict.get(joystick.device_index, dict())
                if event.type == pygame.JOYBUTTONDOWN:
                    event_handler = {"event_type": "button", "index": event.button}
                elif event.type == pygame.JOYAXISMOTION:
                    event_handler = {"event_type": "axis", "index": event.axis}
                else:
                    event_handler = {"event_type": "hat", "index": event.hat, "hat_value": event.value}
                for callback in joystick_handler_dict.get(joystick.search_key(**event_handler), tuple()):
                    callback(event)
            for callback in self.__event_handler_dict.get(event.type, tuple()):
                callback(event)
            for callback in Window.__all_window_event_handler_dict.get(event.type, tuple()):
                callback(event)

    def set_focus(self, obj: Focusable) -> None:
        self.objects.set_focus(obj)

    def remove_focus(self, obj: Focusable) -> None:
        self.objects.remove_focus(obj)

    def handle_focus(self, event: pygame.event.Event) -> None:
        if event.type in [pygame.KEYDOWN, pygame.JOYHATMOTION]:
            Focusable.MODE = Focusable.MODE_KEY if event.type == pygame.KEYDOWN else Focusable.MODE_JOY
            if Window.__all_window_key_enabled and self.__key_enabled:
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
                    key_events = {
                        pygame.KEYDOWN: ("key", side_with_key_event),
                        pygame.JOYHATMOTION: ("value", side_with_joystick_hat_event)
                    }
                    if event.type in key_events:
                        attr, side_dict = key_events[event.type]
                        value = getattr(event, attr)
                        if value in side_dict:
                            self.objects.focus_obj_on_side(side_dict[value])
        else:
            Focusable.MODE = Focusable.MODE_MOUSE

    def after(self, milliseconds: float, callback: Callable[..., Any]) -> WindowCallback:
        window_callback = WindowCallback(callback, milliseconds)
        self.__callback_after.append(window_callback)
        return window_callback

    def remove_window_callback(self, window_callback: WindowCallback) -> None:
        if window_callback in self.__callback_after:
            self.__callback_after.remove(window_callback)

    def bind_event(self, event_type: int, callback: Callable[..., Any]) -> None:
        event_list = self.__event_handler_dict.get(event_type)
        if event_list is None:
            event_list = self.__event_handler_dict[event_type] = list()
        event_list.append(callback)

    @staticmethod
    def bind_event_all_window(event_type: int, callback: Callable[..., Any]) -> None:
        event_list = Window.__all_window_event_handler_dict.get(event_type)
        if event_list is None:
            event_list = Window.__all_window_event_handler_dict[event_type] = list()
        event_list.append(callback)

    def bind_mouse(self, callback: Callable[..., Any]):
        self.__mouse_handler_list.append(callback)

    def bind_key(self, key_value: int, callback: Callable[..., Any], hold: Optional[bool] = False) -> None:
        if not hold:
            key_dict = self.__key_handler_dict
        else:
            key_dict = self.__key_state_dict
        key_list = key_dict.get(key_value)
        if key_list is None:
            key_list = key_dict[key_value] = list()
        key_list.append(callback)

    def bind_joystick(self, joy_id: int, action: str, callback: Callable[..., Any], state: Optional[bool] = False) -> None:
        if not state:
            joystick_handler_dict = self.__joystick_handler_dict
        else:
            joystick_handler_dict = self.__joystick_state_dict
        joystick_dict = joystick_handler_dict.get(joy_id)
        if joystick_dict is None:
            joystick_dict = joystick_handler_dict[joy_id] = dict()
        joystick_list = joystick_dict.get(action)
        if joystick_list is None:
            joystick_list = joystick_dict[action] = list()
        joystick_list.append(callback)

    def screenshot(self) -> None:
        if not self.__screenshot:
            self.__screenshot = True
            i = 1
            while os.path.isfile(os.path.join(sys.path[0], f"screenshot_{i}.png")):
                i += 1
            pygame.image.save(self.surface, os.path.join(sys.path[0], f"screenshot_{i}.png"))
            self.after(1000, self.__hide_screenshot_frame)

    def __hide_screenshot_frame(self) -> None:
        self.__screenshot = False

    def handle_bg_music(self) -> None:
        if (not Window.__enable_music or self.bg_music is None) and pygame.mixer.get_busy():
            self.stop_music()
        elif Window.__enable_music and self.bg_music is not None and (not pygame.mixer.music.get_busy() or Window.__actual_music is None or Window.__actual_music != self.bg_music):
            self.play_music(self.bg_music)

    @staticmethod
    def stop_music() -> None:
        pygame.mixer.music.stop()
        Window.__actual_music = None

    @staticmethod
    def play_music(filepath: str) -> None:
        Window.stop_music()
        if Window.__enable_music:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(Window.__music_volume)
            pygame.mixer.music.play(-1)
            Window.__actual_music = filepath

    @staticmethod
    def play_sound(sound: pygame.mixer.Sound) -> None:
        if Window.__enable_sound and isinstance(sound, pygame.mixer.Sound):
            sound.play()

    @staticmethod
    def sound_volume() -> float:
        return Window.__sound_volume

    @staticmethod
    def music_volume() -> float:
        return Window.__music_volume

    @staticmethod
    def set_sound_volume(value: float) -> None:
        Window.__sound_volume = RESOURCES.set_sfx_volume(value, Window.__enable_sound)

    @staticmethod
    def set_music_volume(value: float) -> None:
        Window.__music_volume = value
        if Window.__music_volume > 1:
            Window.__music_volume = 1
        elif Window.__music_volume < 0:
            Window.__music_volume = 0
        pygame.mixer.music.set_volume(Window.__music_volume)

    @staticmethod
    def set_music_state(state: bool) -> None:
        Window.__enable_music = bool(state)

    @staticmethod
    def set_sound_state(state: bool) -> None:
        Window.__enable_sound = bool(state)
        RESOURCES.set_sfx_volume(Window.__sound_volume, Window.__enable_sound)

    @staticmethod
    def get_music_state() -> bool:
        return Window.__enable_music

    @staticmethod
    def get_sound_state() -> bool:
        return Window.__enable_sound

    @staticmethod
    def load_config() -> None:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        Window.set_music_volume(config.getfloat("MUSIC", "volume", fallback=50) / 100)
        Window.set_music_state(config.getboolean("MUSIC", "enable", fallback=True))
        Window.set_sound_volume(config.getfloat("SFX", "volume", fallback=50) / 100)
        Window.set_sound_state(config.getboolean("SFX", "enable", fallback=True))
        Window.show_fps(config.getboolean("FPS", "show", fallback=False))

    @staticmethod
    def save_config() -> None:
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

    @staticmethod
    def text_input_enabled() -> bool:
        return Window.__text_input_enabled

    @staticmethod
    def enable_text_input(default_rect: pygame.Rect) -> None:
        if not Window.__text_input_enabled:
            pygame.key.start_text_input()
            pygame.key.set_text_input_rect(default_rect)
            Window.__default_key_repeat = pygame.key.get_repeat()
            pygame.key.set_repeat(500, 50)
            Window.__text_input_enabled = True

    @staticmethod
    def disable_text_input() -> None:
        if Window.__text_input_enabled:
            pygame.key.stop_text_input()
            pygame.key.set_repeat(*Window.__default_key_repeat)
            Window.__default_key_repeat = (0, 0)
            Window.__text_input_enabled = False

    @staticmethod
    def create_server(port: int, listen: int) -> Tuple[str, int]:
        Window.__server_socket.bind(port, 1)
        if not Window.__server_socket.connected():
            raise OSError
        Window.connect_to_server("localhost", port, None)
        Window.__server_socket.listen = listen
        return Window.get_server_infos()

    @staticmethod
    def connect_to_server(address: str, port: int, timeout: int) -> bool:
        return Window.__client_socket.connect(address, port, timeout)

    @staticmethod
    def stop_connection() -> None:
        Window.__client_socket.stop()
        Window.__server_socket.stop()

    @property
    def client_socket(self) -> ClientSocket:
        return Window.__client_socket

    @staticmethod
    def get_server_infos() -> Tuple[str, int]:
        return (Window.__server_socket.ip, Window.__server_socket.port)

    @staticmethod
    def get_server_clients_count() -> int:
        return len(Window.__server_socket.clients)

    @staticmethod
    def set_server_listen(listen: int) -> None:
        Window.__server_socket.listen = listen

    surface = property(lambda self: pygame.display.get_surface())
    rect = property(lambda self: self.surface.get_rect())
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