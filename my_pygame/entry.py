# -*- coding: Utf-8 -*

import pygame
from .text import Text
from .shape import RectangleShape
from .clickable import Clickable
from .window import Window

class Entry(Clickable, RectangleShape):
    def __init__(self, master: Window, width=10, font=None, bg=(255, 255, 255), fg=(0, 0, 0),
                 state="normal", highlight_color=(128, 128, 128), hover_sound=None, on_click_sound=None, disabled_sound=None, **kwargs):
        self.__text = Text(font=font, color=fg)
        if width <= 0:
            width = 1
        self.__nb_chars = width
        width, height = self.__text.font.size("|" + "_" * (width))
        self.__cursor_height = height
        RectangleShape.__init__(self, width + 10, height + 10, bg, **kwargs)
        Clickable.__init__(
            self, master, callback=self.start_edit, state=state, highlight_color=highlight_color,
            hover_sound=hover_sound, on_click_sound=on_click_sound, disabled_sound=disabled_sound
        )
        self.__cursor = 0
        self.__show_cursor = False
        self.__cursor_animated = False
        self.__cursor_animation_window_callback = None
        for event in [pygame.KEYDOWN, pygame.TEXTINPUT, pygame.TEXTEDITING]:
            self.master.bind_event(event, self.key_press)
        if self.edit():
            self.start_edit()

    def edit(self) -> bool:
        return self.master.text_input_enabled() and self.has_focus()

    def after_drawing(self, surface: pygame.Surface) -> None:
        RectangleShape.after_drawing(self, surface)
        self.__text.move(left=self.left + 10, centery=self.centery)
        self.__text.draw(surface)
        if self.edit() and self.__show_cursor:
            width = self.__text.font.size(self.__text.message[:self.cursor])[0] + 1
            height = self.__cursor_height
            cursor_start = (self.__text.left + width, self.__text.centery - height // 2)
            cursor_end = (self.__text.left + width, self.__text.centery + height // 2)
            pygame.draw.line(surface, self.__text.color, cursor_start, cursor_end, 2)

    def __animate_cursor(self, milliseconds: float) -> None:
        if not self.edit():
            self.__show_cursor = False
            self.__cursor_animated = False
        else:
            self.__show_cursor = not self.__show_cursor
            self.__cursor_animated = True
            self.__cursor_animation_window_callback = self.master.after(milliseconds, lambda: self.__animate_cursor(milliseconds))

    @property
    def cursor(self) -> int:
        return self.__cursor

    @cursor.setter
    def cursor(self, value: int):
        self.__cursor = int(value)
        if self.__cursor < 0:
            self.__cursor = 0
        elif self.__cursor > len(self.get()):
            self.__cursor = len(self.get())

    def get(self) -> str:
        return self.__text.message

    def start_edit(self) -> None:
        self.master.enable_text_input(self.rect)
        if not self.__cursor_animated:
            self.__animate_cursor(500)

    def stop_edit(self) -> None:
        self.master.disable_text_input()
        self.__show_cursor = False
        self.master.remove_window_callback(self.__cursor_animation_window_callback)

    def move(self, **kwargs) -> None:
        RectangleShape.move(self, **kwargs)
        try:
            if self.edit():
                pygame.key.set_text_input_rect(self.rect)
        except AttributeError:
            pass

    def key_press(self, event: pygame.event.Event) -> None:
        if self.edit():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.__text.message = self.__text.message[:self.cursor - 1] + self.__text.message[self.cursor:]
                    self.cursor -= 1
                elif event.key == pygame.K_DELETE:
                    self.__text.message = self.__text.message[:self.cursor] + self.__text.message[self.cursor + 1:]
                elif event.key == pygame.K_LEFT:
                    self.cursor -= 1
                elif event.key == pygame.K_RIGHT:
                    self.cursor += 1
                elif event.key == pygame.K_HOME:
                    self.cursor = 0
                elif event.key == pygame.K_END:
                    self.cursor = len(self.__text.message)
                self.__show_cursor = True
            elif event.type == pygame.TEXTEDITING:
                if event.length <= self.__nb_chars:
                    self.__text.message = event.text
                    self.cursor = event.start
            elif event.type == pygame.TEXTINPUT:
                new_text = self.__text.message[:self.cursor] + event.text + self.__text.message[self.cursor:]
                if len(new_text) <= self.__nb_chars:
                    self.__text.message = new_text
                    self.cursor += len(event.text)