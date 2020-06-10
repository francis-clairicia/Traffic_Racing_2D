# -*- coding: Utf-8 -*

from typing import Sequence
import pygame
from .abstract import Drawable, Focusable
from .classes import Button

class DrawableList(Drawable):
    def __init__(self, bg_color=(0, 0, 0, 0), offset=0):
        self.__objects = list()
        self.update_pos = True
        self.offset = offset
        self.__bg_color = bg_color
        Drawable.__init__(self)

    def __getitem__(self, index: int):
        return self.__objects[index]

    def __len__(self):
        return len(self.__objects)

    def __iter__(self):
        return iter(self.__objects)

    def __delitem__(self, index: int):
        try:
            obj = self.__objects[index]
        except IndexError:
            pass
        else:
            self.remove_object(obj)

    @property
    def offset(self):
        return self.__offset

    @offset.setter
    def offset(self, value: int):
        self.__offset = int(value)
        self.set_object_pos()

    @property
    def objects(self):
        return tuple(self.__objects)

    def add_object(self, *objects: Sequence[Drawable], update_pos=True):
        for obj in objects:
            if issubclass(type(obj), Drawable) and obj not in self.__objects:
                self.__objects.append(obj)
                setattr(self, "drawable_{}".format(id(obj)), obj)
                if not update_pos:
                    if len(self.__objects) == 1:
                        obj.center = self.center
                    else:
                        self.update_object_pos(obj, self.__objects[-2])
        self.update_image(update_pos)

    def remove_object(self, *objects: Sequence[Drawable], update_pos=True):
        for obj in objects:
            if obj in self.__objects:
                self.__objects.remove(obj)
                delattr(self, "drawable_{}".format(id(obj)))
        self.update_image(update_pos)

    def update_image(self, update_pos: bool):
        self.update_pos = update_pos
        self.set_size(self.get_image_size())
        self.image.fill(self.__bg_color)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            Drawable.draw(self, surface)
            for obj in self.__objects:
                obj.draw(surface)
                if issubclass(type(obj), Focusable):
                    obj.after_drawing(surface)

    def move(self, **kwargs) -> None:
        Drawable.move(self, **kwargs)
        if self.update_pos:
            self.set_object_pos()

    def get_image_size(self) -> tuple:
        return (0, 0)

    def set_object_pos(self) -> None:
        pass

    def update_object_pos(self, obj: Drawable, previous_obj: Drawable) -> None:
        pass

class DrawableListVertical(DrawableList):

    def set_object_pos(self):
        y = 0
        for obj in self.objects:
            obj.move(top=self.y + y, centerx=self.centerx)
            y += obj.height + self.offset

    def update_object_pos(self, obj: Drawable, previous_obj: Drawable) -> None:
        obj.move(top=previous_obj.bottom + self.offset, centerx=previous_obj.centerx)

    def get_image_size(self):
        if len(self.objects) == 0:
            return (0, 0)
        return (
            max(obj.width for obj in self.objects),
            sum(obj.height for obj in self.objects) + (self.offset * (len(self.objects) - 1))
        )

class DrawableListHorizontal(DrawableList):

    def set_object_pos(self):
        x = 0
        for obj in self.objects:
            obj.move(left=self.x + x, centery=self.centery)
            x += obj.width + self.offset

    def update_object_pos(self, obj: Drawable, previous_obj: Drawable) -> None:
        obj.move(left=previous_obj.right + self.offset, centery=previous_obj.centery)

    def get_image_size(self):
        if len(self.objects) == 0:
            return (0, 0)
        return (
            sum(obj.width for obj in self.objects) + (self.offset * (len(self.objects) - 1)),
            max(obj.height for obj in self.objects)
        )

class ButtonListVertical(DrawableListVertical):

    def add_object(self, *buttons: Sequence[Button], update_pos=True):
        DrawableListVertical.add_object(self, *buttons, update_pos=update_pos)
        self.__handle_buttons()
        self.update_image(update_pos)

    def remove_object(self, *buttons: Sequence[Button], update_pos=True):
        DrawableListVertical.remove_object(self, *buttons, update_pos=update_pos)
        self.__handle_buttons()
        self.update_image(update_pos)

    def __handle_buttons(self):
        if len(self.objects) > 0:
            if len(self.objects) == 1:
                self.objects[0].remove_obj_on_side("on_top", "on_bottom")
            else:
                for i, button in enumerate(self.objects):
                    if i == 0:
                        button.remove_obj_on_side("on_top")
                    else:
                        prev = self.objects[i - 1]
                        prev.set_obj_on_side(on_bottom=button)
                        button.set_obj_on_side(on_top=prev)
                        button.remove_obj_on_side("on_bottom")
            size = (
                max(button.width for button in self.objects),
                max(button.height for button in self.objects)
            )
            for button in self.objects:
                button.set_size(size)

class ButtonListHorizontal(DrawableListHorizontal):

    def add_object(self, *buttons: Sequence[Button], update_pos=True):
        DrawableListHorizontal.add_object(self, *buttons, update_pos=update_pos)
        self.__handle_buttons()
        self.update_image(update_pos)

    def remove_object(self, *buttons: Sequence[Button], update_pos=True):
        DrawableListHorizontal.remove_object(self, *buttons, update_pos=update_pos)
        self.__handle_buttons()
        self.update_image(update_pos)

    def __handle_buttons(self):
        if len(self.objects) > 0:
            if len(self.objects) == 1:
                self.objects[0].remove_obj_on_side("on_left", "on_right")
            else:
                for i, button in enumerate(self.objects):
                    if i == 0:
                        button.remove_obj_on_side("on_left")
                    else:
                        prev = self.objects[i - 1]
                        prev.set_obj_on_side(on_right=button)
                        button.set_obj_on_side(on_left=prev)
                        button.remove_obj_on_side("on_right")
            size = (
                max(button.width for button in self.objects),
                max(button.height for button in self.objects)
            )
            for button in self.objects:
                button.set_size(size)