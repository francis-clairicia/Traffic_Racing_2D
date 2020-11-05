# -*- coding: Utf-8 -*

from typing import Optional, Any, Callable
import pygame
from pygame.font import Font
from .image import Image
from .text import Text
from .shape import RectangleShape
from .clickable import Clickable
from .window import Window

class Button(Clickable, RectangleShape):
    def __init__(self, master: Window, text=str(), font=None, img=None, compound="left",
                 callback: Optional[Callable[..., Any]] = None, state="normal",
                 size=None, outline=2, outline_color=(0, 0, 0),
                 bg=(255, 255, 255), fg=(0, 0, 0),
                 hover_bg=(235, 235, 235), hover_fg=None, hover_sound=None,
                 active_bg=(128, 128, 128), active_fg=None, on_click_sound=None,
                 disabled_bg=(128, 128, 128), disabled_fg=(0, 0, 0), disabled_sound=None,
                 disabled_hover_bg=None, disabled_hover_fg=None,
                 disabled_active_bg=None, disabled_active_fg=None,
                 highlight_color=(0, 0, 255),
                 **kwargs):
        self.__text = Text(text, font, fg, justify=Text.T_CENTER, img=img, compound=compound)
        self.__text_offset_move = 0
        self.__text_offset = kwargs.pop("offset", 0)
        if not isinstance(size, (list, tuple)) or len(size) != 2:
            size = (self.__text.w + 20, self.__text.h + 20)
        RectangleShape.__init__(self, *size, color=bg, outline=outline, outline_color=outline_color, **kwargs)
        self.__bg = {
            Clickable.NORMAL: {
                "normal": bg,
                "hover":  bg if hover_bg is None else hover_bg,
                "active": bg if active_bg is None else active_bg
            },
            Clickable.DISABLED: {
                "normal": disabled_bg,
                "hover":  disabled_bg if disabled_hover_bg is None else disabled_hover_bg,
                "active": disabled_bg if disabled_active_bg is None else disabled_active_bg
            }
        }
        self.__fg = {
            Clickable.NORMAL: {
                "normal": fg,
                "hover":  fg if hover_fg is None else hover_fg,
                "active": fg if active_fg is None else active_fg,
            },
            Clickable.DISABLED: {
                "normal": disabled_fg,
                "hover":  disabled_fg if disabled_hover_fg is None else disabled_hover_fg,
                "active": disabled_fg if disabled_active_fg is None else disabled_active_fg
            }
        }
        Clickable.__init__(self, master, callback, state, hover_sound, on_click_sound, disabled_sound, highlight_color=highlight_color)

    @classmethod
    def withImageOnly(cls, master: Window, img: Image, **kwargs):
        kwargs["compound"] = "center"
        return cls(master, img=img, **kwargs)

    @property
    def text(self) -> str:
        return self.__text.message

    @text.setter
    def text(self, string: str) -> None:
        self.__text.message = string
        self.set_size(self.__text.w + 20, self.__text.h + 20)

    @property
    def font(self) -> Font:
        return self.__text.font

    @font.setter
    def font(self, font) -> None:
        self.__text.font = font
        self.set_size(self.__text.w + 20, self.__text.h + 20)

    @property
    def img(self):
        return self.__text.img

    @img.setter
    def img(self, img: Image):
        self.__text.img = img
        self.set_size(self.__text.w + 20, self.__text.h + 20)

    def after_drawing(self, surface: pygame.Surface) -> None:
        RectangleShape.after_drawing(self, surface)
        self.__text.move(center=self.center)
        self.__text.move_ip(0, self.__text_offset_move)
        self.__text.draw(surface)

    def __set_color(self, button_state: str) -> None:
        self.color = self.__bg[self.state][button_state]
        self.__text.color = self.__fg[self.state][button_state]

    def on_hover(self) -> None:
        self.__set_color("active" if self.active else "hover")

    def on_leave(self) -> None:
        self.__set_color("normal")

    def on_active_set(self) -> None:
        self.__set_color("active")
        self.__text_offset_move = self.__text_offset

    def on_active_unset(self) -> None:
        self.__set_color("normal")
        self.__text_offset_move = 0

    def on_change_state(self) -> None:
        if self.hover:
            self.on_hover()
        else:
            self.on_leave()

class ImageButton(Button):

    def __init__(self, master: Window, img: pygame.Surface, hover_img: Optional[pygame.Surface] = None, active_img: Optional[pygame.Surface] = None, size=None, width=None, height=None, rotate=0, offset=3, **kwargs):
        kwargs["bg"] = kwargs["hover_bg"] = kwargs["active_bg"] = kwargs["disabled_bg"] = (0, 0, 0, 0)
        kwargs["outline"] = 0
        kwargs["compound"] = "center"
        kwargs["offset"] = offset
        self.__default_img = Image(img, size=size, width=width, height=height, rotate=rotate)
        self.__hover_img = Image(hover_img, size=size, width=width, height=height, rotate=rotate) if isinstance(hover_img, pygame.Surface) else None
        self.__active_img = Image(active_img, size=size, width=width, height=height, rotate=rotate) if isinstance(active_img, pygame.Surface) else None
        Button.__init__(self, master, img=self.__default_img, **kwargs)

    def on_hover(self):
        Button.on_hover(self)
        if self.__active_img and self.active:
            self.img = self.__active_img
        elif self.__hover_img and self.hover:
            self.img = self.__hover_img
        else:
            self.img = self.__default_img

    def on_active_set(self):
        Button.on_active_set(self)
        if self.__active_img:
            self.img = self.__active_img

    def on_active_unset(self):
        Button.on_active_unset(self)
        self.img = self.__default_img