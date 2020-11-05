# -*- coding: Utf-8 -*

from typing import Tuple, Optional, Any, Union, Callable
import pygame
from pygame.sprite import Sprite
from .vector import Vector2

class Drawable(Sprite):

    def __init__(self, surface: Optional[pygame.Surface] = pygame.Surface((0, 0), flags=pygame.SRCALPHA), rotate=0, **kwargs):
        Sprite.__init__(self)
        self.__surface = self.__mask = None
        self.__rect = pygame.Rect(0, 0, 0, 0)
        self.__x = self.__y = 0
        self.__angle = 0
        self.__former_moves = dict()
        self.__draw_sprite = True
        self.__valid_size = True
        self.__animation_started = False
        self.__animation_params = dict()
        self.image = self.resize_surface(surface, **kwargs)
        self.rotate(rotate)

    @classmethod
    def from_size(cls, size: Tuple[int, int], **kwargs):
        return cls(pygame.Surface(size, flags=pygame.SRCALPHA), **kwargs)

    def __getitem__(self, name: str):
        return getattr(self.rect, name)

    def __setitem__(self, name: str, value: Any):
        self.move(**{name: value})

    def fill(self, color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> None:
        self.image.fill(color)
        self.__mask = pygame.mask.from_surface(self.__surface)

    def blit(self, source, dest, area=None, special_flags=0) -> pygame.Rect:
        rect = self.image.blit(source, dest, area=area, special_flags=special_flags)
        self.__mask = pygame.mask.from_surface(self.image)
        return rect

    def show(self) -> None:
        self.set_visibility(True)

    def hide(self) -> None:
        self.set_visibility(False)

    def set_visibility(self, status: bool) -> None:
        self.__draw_sprite = bool(status)

    def is_shown(self) -> bool:
        return bool(self.__draw_sprite and self.__valid_size)

    @property
    def image(self) -> pygame.Surface:
        return self.__surface

    @image.setter
    def image(self, surface: pygame.Surface) -> None:
        if isinstance(surface, Drawable):
            surface = surface.image
        elif not isinstance(surface, pygame.Surface):
            surface = pygame.Surface((0, 0), flags=pygame.SRCALPHA)
        self.__surface = surface
        self.__rect = self.__surface.get_rect(**self.__former_moves)
        self.mask_update()

    @property
    def rect(self) -> pygame.Rect:
        return self.__rect

    @property
    def mask(self) -> pygame.mask.Mask:
        return self.__mask

    def mask_update(self) -> None:
        self.__mask = pygame.mask.from_surface(self.__surface)

    @property
    def angle(self) -> float:
        return self.__angle

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            self.before_drawing(surface)
            surface.blit(self.image, self.rect)
            self.after_drawing(surface)
            self.focus_drawing(surface)

    def before_drawing(self, surface: pygame.Surface) -> None:
        pass

    def after_drawing(self, surface: pygame.Surface) -> None:
        pass

    def focus_drawing(self, surface: pygame.Surface) -> None:
        pass

    def move(self, **kwargs) -> None:
        if len(kwargs) == 0:
            return
        x = self.__rect.x
        y = self.__rect.y
        common = ("center", "topleft", "topright", "bottomleft", "bottomright", "midtop", "midbottom", "midleft", "midright")
        if not any(key in kwargs for key in ("x", "left", "right", "centerx", *common)):
            kwargs["x"] = x
        if not any(key in kwargs for key in ("y", "top", "bottom", "centery", *common)):
            kwargs["y"] = y
        self.__rect = self.image.get_rect(**kwargs)
        self.__x = self.__rect.x
        self.__y = self.__rect.y
        self.__former_moves = kwargs

    def move_ip(self, x: float, y: float) -> None:
        self.__x += x
        self.__y += y
        self.__rect = self.__surface.get_rect(x=self.__x, y=self.__y)
        self.__former_moves = {"x": self.__x, "y": self.__y}

    def animate_move(self, master, milliseconds: float, speed=1, after_move=None, **kwargs):
        if milliseconds <= 0 or speed <= 0:
            self.move(**kwargs)
        else:
            self.__animation_started = True
            self.__animation_params.update(
                master=master,
                milliseconds=milliseconds,
                speed=speed,
                kwargs=kwargs,
                after_move=after_move
            )
            self.__animate_move(**self.__animation_params)

    def __animate_move(self, master, milliseconds: float, speed: float, kwargs: dict, after_move: Callable[..., Any]) -> None:
        if not self.__animation_started:
            return
        projection = Drawable(self.image)
        projection.move(**kwargs)
        direction = Vector2.from_two_points(self.center, projection.center)
        length = direction.length() - speed
        if length <= 0:
            self.move(**kwargs)
            self.__animation_started = False
            self.__animation_params.clear()
            if callable(after_move):
                after_move()
        else:
            direction.scale_to_length(speed)
            self.move_ip(direction.x, direction.y)
            master.after(milliseconds, lambda: self.__animate_move(**self.__animation_params))

    def animate_move_started(self) -> bool:
        return self.__animation_started

    def animate_move_stop(self):
        self.__animation_started = False

    def animate_move_restart(self):
        if not self.__animation_started and self.__animation_params:
            self.__animation_started = True
            self.__animate_move(**self.__animation_params)

    def rotate(self, angle: float) -> None:
        angle %= 360
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
            self.__angle = (self.__angle + angle) % 360
            if self.__angle < 0:
                self.__angle += 360

    @staticmethod
    def resize_surface(surface: pygame.Surface, size: Optional[Union[int, Tuple[int, int]]] = None,
             width: Optional[int] = None, height: Optional[int] = None,
             min_width: Optional[int] = None, min_height: Optional[int] = None,
             max_width: Optional[int] = None, max_height: Optional[int] = None,
             smooth=True) -> pygame.Surface:
        if smooth:
            scale_func = pygame.transform.smoothscale
        else:
            scale_func = pygame.transform.scale
        w, h = surface.get_size()
        if isinstance(size, (list, tuple)):
            width, height = size
        elif isinstance(size, int):
            width = height = size
        width = round(width) if isinstance(width, (int, float)) else None
        height = round(height) if isinstance(height, (int, float)) else None
        min_width = round(min_width) if isinstance(min_width, (int, float)) else None
        min_height = round(min_height) if isinstance(min_height, (int, float)) else None
        max_width = round(max_width) if isinstance(max_width, (int, float)) else None
        max_height = round(max_height) if isinstance(max_height, (int, float)) else None
        if isinstance(min_width, int):
            width = max(min_width, width, w) if isinstance(width, int) else max(min_width, w)
        elif isinstance(max_width, int):
            width = min(max_width, width, w) if isinstance(width, int) else min(max_width, w)
        if isinstance(min_height, int):
            height = max(min_height, height, h) if isinstance(height, int) else max(min_height, h)
        elif isinstance(max_height, int):
            height = min(max_height, height, h) if isinstance(height, int) else min(max_height, h)
        if isinstance(width, int) and isinstance(height, int):
            surface = scale_func(surface, (width, height))
        elif isinstance(width, int):
            height = 0 if width == 0 else round(h * width / (w if w != 0 else width))
            surface = scale_func(surface, (width, height))
        elif isinstance(height, int):
            width = 0 if height == 0 else round(w * height / (h if h != 0 else height))
            surface = scale_func(surface, (width, height))
        return surface

    def set_size(self, *size: Union[int, Tuple[int, int]], smooth=True) -> None:
        size = size if len(size) == 2 else size[0]
        try:
            self.image = self.resize_surface(self.image, size=size, smooth=smooth)
        except pygame.error:
            self.__valid_size = False
        else:
            self.__valid_size = True

    def set_width(self, width: float, smooth=True)-> None:
        try:
            self.image = self.resize_surface(self.image, width=width, smooth=smooth)
        except pygame.error:
            self.__valid_size = False
        else:
            self.__valid_size = True

    def set_height(self, height: float, smooth=True) -> None:
        try:
            self.image = self.resize_surface(self.image, height=height, smooth=smooth)
        except pygame.error:
            self.__valid_size = False
        else:
            self.__valid_size = True

    left = property(lambda self: self.rect.left, lambda self, value: self.move(left=value))
    right = property(lambda self: self.rect.right, lambda self, value: self.move(right=value))
    top = property(lambda self: self.rect.top, lambda self, value: self.move(top=value))
    bottom = property(lambda self: self.rect.bottom, lambda self, value: self.move(bottom=value))
    x = left
    y = top
    size = property(lambda self: self.rect.size, lambda self, value: self.set_size(value))
    width = property(lambda self: self.rect.width, lambda self, value: self.set_width(value))
    height = property(lambda self: self.rect.height, lambda self, value: self.set_height(value))
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