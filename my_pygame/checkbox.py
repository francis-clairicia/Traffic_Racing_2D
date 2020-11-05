# -*- coding: Utf-8 -*

from typing import Optional, Any, Callable
import pygame
from .shape import RectangleShape
from .image import Image
from .clickable import Clickable
from .window import Window

class CheckBox(Clickable, RectangleShape):
    def __init__(self, master: Window, width: int, height: int, color: tuple, value=False, on_value=True, off_value=False,
                 outline=2, image: Optional[Image] = None, callback: Optional[Callable[..., Any]] = None,
                 highlight_color=(0, 0, 255), state="normal", hover_sound=None, on_click_sound=None, disabled_sound=None, **kwargs):
        RectangleShape.__init__(self, width, height, color, outline=outline, **kwargs)
        Clickable.__init__(self, master, self.change_value, state, highlight_color=highlight_color, hover_sound=hover_sound, on_click_sound=on_click_sound, disabled_sound=disabled_sound)
        self.__on_changed_value = callback
        self.__active_img = image
        self.__on_value = on_value
        self.__off_value = off_value
        if on_value == off_value:
            raise ValueError("'On' value and 'Off' value are identical")
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: Any):
        if value not in [self.__on_value, self.__off_value]:
            return
        self.__value = value
        if callable(self.__on_changed_value):
            self.__on_changed_value(self.__value)

    def after_drawing(self, surface: pygame.Surface) -> None:
        RectangleShape.after_drawing(self, surface)
        if self.value == self.__on_value:
            if isinstance(self.__active_img, Image):
                self.__active_img.center = self.center
                self.__active_img.draw(surface)
            else:
                x, y = self.center
                w, h = self.size
                pygame.draw.line(
                    surface, self.outline_color,
                    (x - (0.7*w)//2, y + (0.7*h)//2),
                    (x + (0.7*w)//2, y - (0.7*h)//2),
                    width=2
                )
                pygame.draw.line(
                    surface, self.outline_color,
                    (x - (0.7*w)//2, y - (0.7*h)//2),
                    (x + (0.7*w)//2, y + (0.7*h)//2),
                    width=2
                )

    def change_value(self):
        self.value = self.__on_value if self.value == self.__off_value else self.__off_value