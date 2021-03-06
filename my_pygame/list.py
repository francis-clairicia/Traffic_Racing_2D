# -*- coding: Utf-8 -*

from typing import Sequence, Iterator, Any
import pygame
from .drawable import Drawable
from .focusable import Focusable
from .shape import RectangleShape
from .colors import TRANSPARENT

class DrawableList:
    def __init__(self, bg_color=None, draw=True):
        self.__bg_color = pygame.Color(bg_color) if bg_color is not None else TRANSPARENT
        self.__list = list()
        self.__index = -1
        self.__draw = draw

    def __len__(self) -> int:
        return len(self.__list)

    def __iter__(self) -> Iterator[Drawable]:
        return iter(self.__list)

    def __getitem__(self, index: int) -> Drawable:
        return self.__list[index]

    def __contains__(self, value: Any) -> bool:
        return bool(value in self.__list)

    @property
    def rect(self) -> pygame.Rect:
        left = min((obj.left for obj in self.__list), default=0)
        right = max((obj.right for obj in self.__list), default=0)
        top = min((obj.top for obj in self.__list), default=0)
        bottom = max((obj.bottom for obj in self.__list), default=0)
        width = right - left
        height = bottom - top
        return pygame.Rect(left, top, width, height)

    @property
    def end(self) -> int:
        return len(self.__list)

    @property
    def bg_color(self) -> pygame.Color:
        return self.__bg_color

    def add(self, obj: Drawable, *objs: Drawable) -> None:
        for obj in [obj, *objs]:
            if isinstance(obj, (Drawable, DrawableList)) and obj not in self.__list:
                self.__list.append(obj)

    def remove(self, *obj_list: Drawable) -> None:
        for obj in obj_list:
            if obj in self.__list:
                self.__list.remove(obj)
        self.__update_index()

    def remove_from_index(self, index: int) -> None:
        if index in range(len(self.__list)):
            self.__list.pop(index)
            self.__update_index()

    def clear(self) -> None:
        self.__list.clear()
        self.__index = -1

    def empty(self) -> bool:
        if self.__list:
            return False
        return True

    def set_priority(self, obj: Drawable, new_pos: int, relative_to=None) -> None:
        former_pos = self.__list.index(obj)
        self.__list.pop(former_pos)
        if relative_to:
            new_pos += self.__list.index(relative_to)
        self.__list.insert(new_pos, obj)

    def __update_index(self) -> None:
        size = len(self.focusable)
        if self.__index >= size:
            self.__index = size - 1

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown() and self.__draw:
            self.before_drawing(surface)
            if self.__bg_color and self.__bg_color != TRANSPARENT:
                pygame.draw.rect(surface, self.__bg_color, self.rect)
            for obj in self.__list:
                obj.draw(surface)
            self.after_drawing(surface)

    def before_drawing(self, surface: pygame.Surface) -> None:
        pass

    def after_drawing(self, surface: pygame.Surface) -> None:
        pass

    def update(self, *args, **kwargs) -> None:
        for obj in self.__list:
            obj.update(*args, **kwargs)

    def move(self, **kwargs) -> None:
        pass

    def move_ip(self, x: float, y: float) -> None:
        for obj in self.__list:
            obj.move_ip(x, y)

    def focus_get(self) -> Focusable:
        if self.__index < 0:
            return None
        return self.focusable[self.__index]

    def focus_next(self) -> None:
        if any(obj.take_focus() for obj in self.focusable):
            size = len(self.focusable)
            while True:
                self.__index = (self.__index + 1) % size
                obj = self.focus_get()
                if obj.take_focus():
                    break
            self.set_focus(obj)
        else:
            self.__index = -1

    def focus_obj_on_side(self, side: str) -> None:
        actual_obj = self.focus_get()
        if actual_obj is None:
            self.focus_next()
        else:
            obj = actual_obj.get_obj_on_side(side)
            while obj and not obj.take_focus():
                obj = obj.get_obj_on_side(side)
            if obj:
                self.set_focus(obj)

    def set_focus(self, obj: Focusable) -> None:
        if obj is not None and obj not in self.focusable:
            return
        for obj_f in self.focusable:
            obj_f.focus = False
        if isinstance(obj, Focusable):
            obj.focus = True
            self.__index = self.focusable.index(obj)
        else:
            self.__index = -1

    def remove_focus(self, obj: Focusable) -> None:
        if obj not in self.focusable:
            return
        obj.focus = False
        if self.focus_get() == obj:
            self.set_focus(None)

    def focus_mode_update(self) -> None:
        if Focusable.MODE != Focusable.MODE_MOUSE and self.focus_get() is None:
            self.focus_next()

    def show(self) -> None:
        for obj in self.__list:
            obj.show()

    def hide(self) -> None:
        for obj in self.__list:
            obj.hide()

    def set_visibility(self, status: bool) -> None:
        for obj in self.__list:
            obj.set_visibility(status)

    def is_shown(self) -> bool:
        return any(obj.is_shown() for obj in self.__list)

    @property
    def list(self) -> Sequence[Drawable]:
        return tuple(self.__list)

    @property
    def index(self) -> int:
        return self.__index

    @property
    def focusable(self) -> Sequence[Focusable]:
        focusable_list = list()
        for obj in self.__list:
            if isinstance(obj, Focusable):
                focusable_list.append(obj)
            elif isinstance(obj, DrawableList):
                focusable_list.extend(obj.focusable)
        return focusable_list

    @property
    def drawable(self) -> Sequence[Drawable]:
        drawable_list = list()
        for obj in self.__list:
            if isinstance(obj, Drawable):
                drawable_list.append(obj)
            elif isinstance(obj, DrawableList):
                drawable_list.extend(obj.drawable)
        return drawable_list

    left = property(lambda self: self.rect.left, lambda self, value: self.move(left=value))
    right = property(lambda self: self.rect.right, lambda self, value: self.move(right=value))
    top = property(lambda self: self.rect.top, lambda self, value: self.move(top=value))
    bottom = property(lambda self: self.rect.bottom, lambda self, value: self.move(bottom=value))
    x = left
    y = top
    size = property(lambda self: self.rect.size)
    width = property(lambda self: self.rect.width)
    height = property(lambda self: self.rect.height)
    w = width
    h = height
    center = property(lambda self: self.rect.center, lambda self, value: self.move(center=value))
    centerx = property(lambda self: self.rect.centerx, lambda self, value: self.move(centerx=value))
    centery = property(lambda self: self.rect.centery, lambda self, value: self.move(centery=value))
    topleft = property(lambda self: self.rect.topleft, lambda self, value: self.move(topleft=value))
    topright = property(lambda self: self.rect.topright, lambda self, value: self.move(topright=value))
    bottomleft = property(lambda self: self.rect.bottomleft, lambda self, value: self.move(bottomleft=value))
    bottomright = property(lambda self: self.rect.bottomright, lambda self, value: self.move(bottomright=value))
    midtop = property(lambda self: self.rect.midtop, lambda self, value: self.move(midtop=value))
    midbottom = property(lambda self: self.rect.midbottom, lambda self, value: self.move(midbottom=value))
    midleft = property(lambda self: self.rect.midleft, lambda self, value: self.move(midleft=value))
    midright = property(lambda self: self.rect.midright, lambda self, value: self.move(midright=value))

class AbstractDrawableListAligned(DrawableList):

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    def __init__(self, offset: int, orient: str, bg_color=None, draw=True, justify="center"):
        DrawableList.__init__(self, bg_color=bg_color, draw=draw)
        self.__background = Drawable()
        self.offset = offset
        values = {
            AbstractDrawableListAligned.HORIZONTAL: ("left", "right",),
            AbstractDrawableListAligned.VERTICAL: ("top", "bottom")
        }
        self.__start, self.__end = values[orient]
        justify_dict = {
            AbstractDrawableListAligned.HORIZONTAL: {
                "top": "top",
                "bottom": "bottom",
                "center": "centery"
            },
            AbstractDrawableListAligned.VERTICAL: {
                "left": "left",
                "right": "right",
                "center": "centerx"
            }
        }
        self.__justify = justify_dict[orient][justify]

    def add(self, obj: Drawable, *objs: Drawable) -> None:
        DrawableList.add(self, obj, *objs)
        self.__align_all_objects()

    def remove(self, obj: Drawable, *objs: Drawable) -> None:
        DrawableList.remove(self, obj, *objs)
        self.__align_all_objects()

    def remove_from_index(self, index: int) -> None:
        DrawableList.remove_from_index(self, index)
        self.__align_all_objects()

    def move(self, **kwargs) -> None:
        if self.list:
            self.__background.set_size(self.size)
            self.__background.move(**kwargs)
            self.list[0].move(**{self.__start: self.__background[self.__start]})
            self.list[0].move(**{self.__justify: self.__background[self.__justify]})
            self.__align_all_objects()
            DrawableList.move(self)

    def __align_all_objects(self) -> None:
        for obj_1, obj_2 in zip(self.list[:-1], self.list[1:]):
            obj_2.move(**{self.__start: getattr(obj_1.rect, self.__end, 0) + self.offset})
        for obj in self.list:
            obj.move(**{self.__justify: getattr(self.list[0].rect, self.__justify, 0)})

class DrawableListVertical(AbstractDrawableListAligned):

    def __init__(self, offset: int, bg_color=None, draw=True, justify="center"):
        AbstractDrawableListAligned.__init__(self, offset, AbstractDrawableListAligned.VERTICAL, bg_color=bg_color, draw=draw, justify=justify)

class DrawableListHorizontal(AbstractDrawableListAligned):

    def __init__(self, offset: int, bg_color=None, draw=True, justify="center"):
        AbstractDrawableListAligned.__init__(self, offset, AbstractDrawableListAligned.HORIZONTAL, bg_color=bg_color, draw=draw, justify=justify)

class ButtonListVertical(DrawableListVertical):

    def add(self, button: Focusable, *buttons: Focusable) -> None:
        DrawableListVertical.add(self, button, *buttons)
        self.__handle_buttons()

    def remove(self, button: Focusable, *buttons: Focusable) -> None:
        DrawableListVertical.remove(self, button, *buttons)
        self.__handle_buttons()

    def remove_from_index(self, index: int) -> None:
        DrawableListVertical.remove_from_index(self, index)
        self.__handle_buttons()

    def __handle_buttons(self) -> None:
        if len(self.list) > 0:
            for i, button in enumerate(self.list):
                if i == 0:
                    button.remove_obj_on_side(Focusable.ON_TOP)
                else:
                    prev = self.list[i - 1]
                    prev.set_obj_on_side(on_bottom=button)
                    button.set_obj_on_side(on_top=prev)
                button.remove_obj_on_side(Focusable.ON_BOTTOM)
            size = (
                max(button.width for button in self.list),
                max(button.height for button in self.list)
            )
            for button in self.list:
                button.set_size(size)

    def set_obj_on_side(self, on_top=None, on_bottom=None, on_left=None, on_right=None) -> None:
        if len(self.list) > 0:
            self.list[0].set_obj_on_side(on_top=on_top)
            self.list[-1].set_obj_on_side(on_bottom=on_bottom)
            for obj in self.list:
                obj.set_obj_on_side(on_left=on_left, on_right=on_right)

    def remove_obj_on_side(self, *sides: str) -> None:
        if len(self.list) > 0:
            if Focusable.ON_TOP in sides:
                self.list[0].remove_obj_on_side(Focusable.ON_TOP)
            if Focusable.ON_BOTTOM in sides:
                self.list[-1].remove_obj_on_side(Focusable.ON_BOTTOM)
            for obj in self.list:
                obj.remove_obj_on_side(*filter(lambda side: side in (Focusable.ON_LEFT, Focusable.ON_RIGHT), sides))

class ButtonListHorizontal(DrawableListHorizontal):

    def add(self, button: Focusable, *buttons: Focusable) -> None:
        DrawableListHorizontal.add(self, button, *buttons)
        self.__handle_buttons()

    def remove(self, button: Focusable, *buttons: Focusable) -> None:
        DrawableListHorizontal.remove(self, button, *buttons)
        self.__handle_buttons()

    def remove_from_index(self, index: int) -> None:
        DrawableListHorizontal.remove_from_index(self, index)
        self.__handle_buttons()

    def __handle_buttons(self) -> None:
        if len(self.list) > 0:
            for i, button in enumerate(self.list):
                if i == 0:
                    button.remove_obj_on_side(Focusable.ON_LEFT)
                else:
                    prev = self.list[i - 1]
                    prev.set_obj_on_side(on_right=button)
                    button.set_obj_on_side(on_left=prev)
                button.remove_obj_on_side(Focusable.ON_RIGHT)
            size = (
                max(button.width for button in self.list),
                max(button.height for button in self.list)
            )
            for button in self.list:
                button.set_size(size)

    def set_obj_on_side(self, on_top=None, on_bottom=None, on_left=None, on_right=None) -> None:
        if len(self.list) > 0:
            self.list[0].set_obj_on_side(on_left=on_left)
            self.list[-1].set_obj_on_side(on_right=on_right)
            for obj in self.list:
                obj.set_obj_on_side(on_top=on_top, on_bottom=on_bottom)

    def remove_obj_on_side(self, *sides: str) -> None:
        if len(self.list) > 0:
            if Focusable.ON_LEFT in sides:
                self.list[0].remove_obj_on_side(Focusable.ON_LEFT)
            if Focusable.ON_RIGHT in sides:
                self.list[-1].remove_obj_on_side(Focusable.ON_RIGHT)
            for obj in self.list:
                obj.remove_obj_on_side(*filter(lambda side: side in (Focusable.ON_TOP, Focusable.ON_BOTTOM), sides))