# -*- coding: Utf-8 -*

from .window import Window
from .text import Text
from .shape import RectangleShape
from .colors import WHITE, BLACK

class Loading(Window):
    def __init__(self, text="Loading...", font=("calibri", 300), bg=BLACK, opening=True, ending=True, side_opening="left", side_ending="right"):
        Window.__init__(self, bg_color=None)
        self.master = None
        speed = 50
        self.animation_opening = {
            "left": lambda x=speed, y=0: self._show_animation(x, y),
            "right": lambda x=-speed, y=0: self._show_animation(x, y),
            "top": lambda x=0, y=speed: self._show_animation(x, y),
            "bottom": lambda x=0, y=-speed: self._show_animation(x, y)
        }
        self.animation_init_opening = {
            "left": {"right": self.left - 1, "centery": self.centery},
            "right": {"left": self.right + 1, "centery": self.centery},
            "top": {"bottom": self.top - 1, "centerx": self.centerx},
            "bottom": {"top": self.bottom + 1, "centerx": self.centerx}
        }
        self.rectangle = RectangleShape(self.w, self.h, bg)
        self.text = Text(text, font, WHITE)
        self.animation_ending = {
            "left": lambda x=-speed, y=0: self._hide_animation(x, y),
            "right": lambda x=speed, y=0: self._hide_animation(x, y),
            "top": lambda x=0, y=-speed: self._hide_animation(x, y),
            "bottom": lambda x=0, y=speed: self._hide_animation(x, y)
        }
        self.opening = opening
        self.ending = ending
        self.side_opening = side_opening
        self.side_ending = side_ending

    def show(self, master: Window):
        self.master = master
        if not self.opening:
            self.rectangle.move(x=0, y=0)
            self.text.move(center=self.rectangle.center)
            self.draw_screen()
            self.refresh()
        else:
            self.rectangle.move(**self.animation_init_opening[self.side_opening])
            self.text.move(center=self.rectangle.center)
            self.after(0, self.animation_opening[self.side_opening])
            self.mainloop()

    def hide(self, master: Window):
        self.master = master
        if not self.ending:
            self.draw_screen()
            self.refresh()
        else:
            self.master.place_objects()
            self.after(0, self.animation_ending[self.side_ending])
            self.mainloop(fill_bg=False)

    def _show_animation(self, x_offset: int, y_offset: int):
        self.rectangle.rect.move_ip(x_offset, y_offset)
        self.text.move(center=self.rectangle.center)
        self.master.draw_screen()
        side = self.side_opening
        if (side == "left" and self.rectangle.left > self.left) \
        or (side == "right" and self.rectangle.right < self.right) \
        or (side == "top" and self.rectangle.top > self.top) \
        or (side == "bottom" and self.rectangle.bottom < self.bottom):
            self.rectangle.move(x=0, y=0)
            self.draw_screen()
            self.refresh()
            self.stop()
        else:
            self.after(10, lambda x=x_offset, y=y_offset: self._show_animation(x, y))

    def _hide_animation(self, x_offset: int, y_offset: int):
        self.rectangle.rect.move_ip(x_offset, y_offset)
        self.text.move(center=self.rectangle.center)
        self.master.draw_screen()
        if not self.rect.colliderect(self.rectangle.rect):
            self.stop()
        else:
            self.after(10, lambda x=x_offset, y=y_offset: self._hide_animation(x, y))