# -*- coding: Utf-8 -*

import os
import sys
from typing import Callable, Any, Union
import pygame
from .abstract import Drawable, Focusable
from .classes import Text, RectangleShape
from .joystick import Joystick
from .keyboard import Keyboard
from .clock import Clock

CONFIG_FILE = os.path.join(sys.path[0], "settings.conf")

class MetaWindow(type):
    def __call__(cls, *args, **kwargs):
        window = type.__call__(cls, *args, **kwargs)
        window.after_init()
        return window

class WindowCallback(object):
    def __init__(self, callback: Callable[..., Any], wait_time: float):
        self.wait_time = wait_time
        self.callback = callback
        self.clock = Clock()

    def can_call(self) -> bool:
        return self.clock.elapsed_time(self.wait_time, restart=False)

    def __call__(self):
        return self.callback()

class Window(metaclass=MetaWindow):

    __all_opened = list()
    __sound_volume = 0.5
    __music_volume = 0.5
    __enable_music = True
    __enable_sound = True
    actual_music = None
    __show_fps = False
    __fps = 60
    __fps_obj = None
    joystick = list()
    keyboard = Keyboard()

    def __init__(self, master=None, size=(0, 0), flags=0, bg_color=(0, 0, 0), bg_music=None):
        Window.init_pygame(size, flags)
        self.__master = master
        self.window = pygame.display.get_surface()
        self.rect = self.window.get_rect()
        self.main_clock = pygame.time.Clock()
        self.loop = False
        self.objects = list()
        self.focusable_objects = list()
        self.focusable_objects_idx = -1
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
            pygame.JOYBUTTONDOWN,
            pygame.JOYBUTTONUP,
            pygame.JOYAXISMOTION,
            pygame.JOYHATMOTION
        )
        mouse_show_event = (
            pygame.KEYDOWN,
            pygame.KEYUP,
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

    def after_init(self):
        self.place_objects()
        self.set_grid()

    @staticmethod
    def init_pygame(size=(0, 0), flags=0):
        if not pygame.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 512)
            status = pygame.init()
            if status[1] > 0:
                print("Error on pygame initialization ({} modules failed to load)".format(status[1]), file=sys.stderr)
                sys.exit(84)
            Window.load_sound_volume_from_save()
        if pygame.display.get_surface() is None:
            if size[0] <= 0 or size[1] <= 0:
                video_info = pygame.display.Info()
                size = video_info.current_w, video_info.current_h
            pygame.display.set_mode(tuple(size), flags)

    # @classmethod
    # def withLoading(cls, text="Loading...", font=("calibri", 300), bg=(0, 0, 0), fg=(255, 255, 255),
    #                 opening=True, ending=True, side_opening="left", side_ending="right", speed=50,
    #                 *args, **kwargs):
    #     Window.init_pygame(kwargs.get("size", (0, 0)), kwargs.get("flags", 0))
    #     kwargs.pop("size", None)
    #     kwargs.pop("flags", None)
    #     window = pygame.display.get_surface()
    #     window_rect = window.get_rect()
    #     rectangle = RectangleShape(*window_rect.size, color=bg)
    #     Text(text, font, fg, center=rectangle.center).draw(rectangle)
    #     animation_init_opening = {
    #         "left": {"right": window_rect.left - 1, "centery": window_rect.centery},
    #         "right": {"left": window_rect.right + 1, "centery": window_rect.centery},
    #         "top": {"bottom": window_rect.top - 1, "centerx": window_rect.centerx},
    #         "bottom": {"top": window_rect.bottom + 1, "centerx": window_rect.centerx}
    #     }
    #     animation_opening = {
    #         "left": (speed, 0),
    #         "right": (-speed, 0),
    #         "top": (0, speed),
    #         "bottom": (0, -speed)
    #     }
    #     animation_ending = {
    #         "left": (-speed, 0),
    #         "right": (speed, 0),
    #         "top": (0, -speed),
    #         "bottom": (0, speed)
    #     }
    #     rectangle.move(**animation_init_opening[side_opening])
    #     window_to_hide = window.copy()
    #     clock = Clock()
    #     while True:
    #         if clock.elapsed_time(10):
    #             rectangle.move_ip(*animation_opening[side_opening])
    #             if (side_opening == "left" and rectangle.left > window_rect.left) \
    #             or (side_opening == "right" and rectangle.right < window_rect.right) \
    #             or (side_opening == "top" and rectangle.top > window_rect.top) \
    #             or (side_opening == "bottom" and rectangle.bottom < window_rect.bottom) \
    #             or (not opening):
    #                 rectangle.move(x=0, y=0)
    #                 opening = False
    #             window.blit(window_to_hide, window_rect)
    #             rectangle.draw(window)
    #             pygame.display.flip()
    #             if not opening:
    #                 break
    #     new_window = cls(*args, **kwargs)
    #     while True:
    #         if clock.elapsed_time(10):
    #             rectangle.move_ip(*animation_ending[side_ending])
    #             ending = bool(window_rect.colliderect(rectangle.rect))
    #             new_window.draw_screen(show_fps=False)
    #             rectangle.draw(window)
    #             pygame.display.flip()
    #             if not ending:
    #                 break
    #     return new_window

    @property
    def main_window(self) -> bool:
        return bool(Window.__all_opened[0] == self)

    @staticmethod
    def set_joystick(nb_joysticks: int):
        for i in range(nb_joysticks):
            if i >= len(Window.joystick):
                Window.joystick.append(Joystick(i))
        while len(Window.joystick) > nb_joysticks:
            del Window.joystick[-1]

    def __setattr__(self, name, obj):
        if issubclass(type(obj), Drawable):
            if hasattr(self, name):
                delattr(self, name)
            self.add(obj)
        return object.__setattr__(self, name, obj)

    def __delattr__(self, name):
        obj = getattr(self, name)
        if issubclass(type(obj), Drawable):
            self.remove(obj)
        return object.__delattr__(self, name)

    def __contains__(self, obj):
        return bool(obj in self.objects)

    def add(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)

    def remove(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
        self.focus_remove(obj)

    def focus_add(self, obj):
        if issubclass(type(obj), Focusable):
            self.focusable_objects.append(obj)

    def focus_remove(self, obj):
        if obj in self.focusable_objects:
            self.focusable_objects.remove(obj)
            if self.focusable_objects_idx >= len(self.focusable_objects):
                self.focusable_objects_idx = len(self.focusable_objects) - 1

    @property
    def end_obj_list(self):
        return len(self.objects)

    def set_object_priority(self, obj, new_pos, relative_to=None):
        former_pos = self.objects.index(obj)
        del self.objects[former_pos]
        if relative_to:
            new_pos += self.objects.index(relative_to)
        self.objects.insert(new_pos, obj)

    def set_focus(self, obj: Focusable) -> None:
        if self.focusable_objects_idx >= 0:
            self.focusable_objects[self.focusable_objects_idx].focus_leave()
        try:
            if obj is None:
                raise ValueError
            self.focusable_objects_idx = self.focusable_objects.index(obj)
            obj.focus_set(from_master=True)
        except ValueError:
            self.focusable_objects_idx = -1
        for obj_f in self.focusable_objects:
            if obj_f != obj and obj_f.has_focus():
                obj_f.focus_leave()

    def focus_next(self) -> Union[Focusable, None]:
        if all(not obj.is_shown() or not obj.take_focus() for obj in self.focusable_objects):
            return None
        i = 0
        while True:
            i += 1
            obj = self.focusable_objects[(self.focusable_objects_idx + i) % len(self.focusable_objects)]
            if obj.is_shown() and obj.take_focus():
                break
        return obj

    def enable_key_joy_focus(self):
        self.__key_enabled = True

    def disable_key_joy_focus(self):
        self.__key_enabled = False

    @staticmethod
    def set_icon(icon_filepath):
        icon = pygame.image.load(icon_filepath).convert_alpha()
        pygame.display.set_icon(icon)

    @staticmethod
    def set_title(title: str):
        pygame.display.set_caption(title)

    def mainloop(self):
        self.loop = True
        Window.__all_opened.append(self)
        if Focusable.MODE != Focusable.MODE_MOUSE and self.focusable_objects_idx < 0:
            self.set_focus(self.focus_next())
        while self.loop:
            for callback in [c for c in self.callback_after if c.can_call()]:
                callback()
                self.callback_after.remove(callback)
            self.fps_update()
            self.update()
            self.keyboard.update()
            for joystick in self.joystick:
                joystick.update()
            for obj in self.focusable_objects:
                obj.focus_update()
            self.draw_and_refresh()
            self.event_handler()
            self.update_sound_volume()
            self.check_sound_status()

    def stop(self, force=False, sound=None):
        self.loop = False
        self.on_quit()
        if sound:
            self.play_sound(sound)
        if self.main_window or force is True:
            Window.save_sound_volume()
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
            self.window.fill(self.bg_color)
        if isinstance(self.__master, Window):
            self.__master.draw_screen(show_fps=False)
        for obj in self.objects:
            obj.draw(self.window)
            if issubclass(type(obj), Focusable):
                obj.after_drawing(self.window)
        if Window.__show_fps is True and show_fps:
            Window.__fps_obj.draw(self.window)
        if self.__screenshot:
            pygame.draw.rect(self.window, (255, 255, 255), self.rect, width=30)

    @staticmethod
    def set_fps(framerate: int) -> None:
        Window.__fps = int(framerate)

    @staticmethod
    def show_fps(status: bool, **kwargs):
        Window.__show_fps = bool(status)
        Window.__fps_obj.config(**kwargs)

    @staticmethod
    def move_fps_object(**kwargs):
        Window.__fps_obj.move(**kwargs)

    @staticmethod
    def fps_is_shown() -> bool:
        return Window.__show_fps

    def fps_update(self):
        self.main_clock.tick(Window.__fps)
        Window.__fps_obj.txt = f"{round(self.main_clock.get_fps())} FPS"

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
                        callback(self.joystick[joy_id][id_])
        for event in pygame.event.get():
            if event.type == pygame.QUIT \
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_F4 and (event.mod & pygame.KMOD_LALT)):
                self.stop(force=True)
            elif event.type == pygame.KEYDOWN:
                for callback in self.key_handler_dict.get(event.key, tuple()):
                    callback(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                for callback in self.joystick_handler_dict.get(event.joy, dict()).get(self.joystick[event.joy].search_key("button", event.button), tuple()):
                    callback(event)
            for callback in self.event_handler_dict.get(event.type, tuple()):
                callback(event)

    def handle_focus(self, event: pygame.event.Event) -> None:
        if event.type in [pygame.KEYDOWN, pygame.JOYHATMOTION]:
            Focusable.MODE = Focusable.MODE_KEY if event.type == pygame.KEYDOWN else Focusable.MODE_JOY
            if self.__key_enabled and any(obj.is_shown() for obj in self.focusable_objects):
                obj = None
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
                    obj = self.focus_next()
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
                            if self.focusable_objects_idx < 0:
                                obj = self.focusable_objects[0]
                            else:
                                obj = self.focusable_objects[self.focusable_objects_idx].get_obj_on_side(side_dict[value])
                            break
                    while obj and (not obj.is_shown() or not obj.take_focus()):
                        obj = obj.get_obj_on_side(side_dict[value])
                if obj:
                    self.set_focus(obj)
        else:
            Focusable.MODE = Focusable.MODE_MOUSE

    def after(self, milliseconds: float, callback: Callable[..., Any]):
        self.callback_after.append(WindowCallback(callback, milliseconds))

    def bind_event(self, event_type, callback):
        event_list = self.event_handler_dict.get(event_type)
        if event_list is None:
            event_list = self.event_handler_dict[event_type] = list()
        event_list.append(callback)

    def bind_mouse(self, callback):
        self.mouse_handler_list.append(callback)

    def bind_key(self, key_value, callback, hold=False):
        if not hold:
            key_dict = self.key_handler_dict
        else:
            key_dict = self.key_state_dict
        key_list = key_dict.get(key_value)
        if key_list is None:
            key_list = key_dict[key_value] = list()
        key_list.append(callback)

    def bind_joystick_button(self, joy_id, button_id, callback):
        joystick_dict = self.joystick_handler_dict.get(joy_id)
        if joystick_dict is None:
            joystick_dict = self.joystick_handler_dict[joy_id] = dict()
        joystick_list = joystick_dict.get(button_id)
        if joystick_list is None:
            joystick_list = joystick_dict[button_id] = list()
        joystick_list.append(callback)

    def bind_joystick_axis(self, joy_id, axis_id, callback):
        self.bind_joystick_button(joy_id, axis_id, callback)

    def screenshot(self):
        if not self.__screenshot:
            self.__screenshot = True
            i = 1
            while os.path.isfile(os.path.join(sys.path[0], f"screenshot_{i}.png")):
                i += 1
            pygame.image.save(self.window, os.path.join(sys.path[0], f"screenshot_{i}.png"))
            self.after(1000, self.__hide_screenshot_frame)

    def __hide_screenshot_frame(self):
        self.__screenshot = False

    def check_sound_status(self):
        if not Window.__enable_music or (self.bg_music is None and pygame.mixer.get_busy()):
            self.stop_music()
        elif Window.__enable_music and self.bg_music and (not pygame.mixer.music.get_busy() or Window.actual_music is None or Window.actual_music != self.bg_music):
            self.play_music(self.bg_music)

    def update_sound_volume(self):
        for obj in self.objects:
            for sound in obj.sounds:
                sound.set_volume(Window.__sound_volume if Window.__enable_sound else 0)

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
    def play_sound(filepath: str):
        if Window.__enable_sound:
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(Window.__sound_volume)
            sound.play()

    @staticmethod
    def sound_volume():
        return Window.__sound_volume

    @staticmethod
    def music_volume():
        return Window.__music_volume

    @staticmethod
    def set_sound_volume(value: float):
        Window.__sound_volume = value
        if Window.__sound_volume > 1:
            Window.__sound_volume = 1
        elif Window.__sound_volume < 0:
            Window.__sound_volume = 0

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

    @staticmethod
    def get_music_state() -> bool:
        return Window.__enable_music

    @staticmethod
    def get_sound_state() -> bool:
        return Window.__enable_sound

    @staticmethod
    def load_sound_volume_from_save():
        pygame.mixer.music.set_volume(Window.__music_volume)
        if not os.path.isfile(CONFIG_FILE):
            return
        with open(CONFIG_FILE, "r") as file:
            config = file.read()
        for line in config.splitlines():
            try:
                key, value = line.split("=")
                if key == "music":
                    Window.set_music_volume(float(value) / 100)
                if key == "sound":
                    Window.set_sound_volume(float(value) / 100)
                if key == "enable_music":
                    Window.set_music_state(int(value))
                if key == "enable_sound":
                    Window.set_sound_state(int(value))
            except ValueError:
                continue

    @staticmethod
    def save_sound_volume():
        variables = {
            "music": round(Window.__music_volume * 100),
            "sound": round(Window.__sound_volume * 100),
            "enable_music": 1 if Window.get_music_state() else 0,
            "enable_sound": 1 if Window.get_sound_state() else 0,
        }
        config = str()
        for key, value in variables.items():
            config += f"{key}={value}\n"
        with open(CONFIG_FILE, "w") as file:
            file.write(config)

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