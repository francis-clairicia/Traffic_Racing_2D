# -*- coding: Utf-8 -*

from typing import Tuple, Optional, Any, Union, List, Callable
import pygame
from pygame.event import Event
from pygame.sprite import Sprite, Group

class Drawable(Sprite):

    __slots__ = (
        "__surface",
        "__rect",
        "__mask",
        "__rotate",
        "__sounds",
        "__sub_drawables",
        "__former_movs",
        "__draw_sprite",
        "__valid_size",
    )

    def __init__(self, surface: Optional[pygame.Surface] = pygame.Surface((0, 0), flags=pygame.SRCALPHA),
                 rotate: Optional[int] = 0, groups: Optional[Union[List[Group], Tuple[Group, ...]]] = tuple(), **kwargs):
        Sprite.__init__(self, *groups)
        self.__surface = self.__rect = self.__mask = None
        self.__rotate = 0
        self.__sounds = list()
        self.__sub_drawables = list()
        self.__former_moves = dict()
        self.__draw_sprite = True
        self.__valid_size = True
        self.image = surface
        self.rotate = rotate
        self.move(**kwargs)

    def __setattr__(self, name: str, value: Any):
        if isinstance(value, pygame.mixer.Sound):
            if hasattr(self, name):
                s = getattr(self, name)
                if s in self.__sounds:
                    self.__sounds.remove(s)
            self.__sounds.append(value)
        elif issubclass(type(value), Drawable):
            self.__sub_drawables.append(value)
        return object.__setattr__(self, name, value)

    def __delattr__(self, name: str):
        obj = getattr(self, name)
        if obj in self.__sub_drawables:
            self.__sub_drawables.remove(obj)
        elif obj in self.__sounds:
            self.__sounds.remove(obj)
        return object.__delattr__(self, name)

    def __getitem__(self, name: str):
        return getattr(self.rect, name)

    def __setitem__(self, name: str, value: Any):
        self.move(**{name: value})

    def fill(self, color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> None:
        self.image.fill(color)

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
        self.__surface = surface
        self.__rect = self.__surface.get_rect()
        self.move(**self.__former_moves)
        self.__mask = pygame.mask.from_surface(self.__surface)

    @property
    def rect(self):
        return self.__rect

    @property
    def mask(self):
        return self.__mask

    @property
    def sounds(self) -> Tuple[pygame.mixer.Sound, ...]:
        sounds = self.__sounds.copy()
        for obj in self.__sub_drawables:
            sounds.extend(obj.sounds)
        return tuple(sounds)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            surface.blit(self.image, self.rect)

    def move(self, **kwargs) -> None:
        if len(kwargs) == 0:
            return
        x = self.__rect.x if isinstance(self.__rect, pygame.Rect) else 0
        y = self.__rect.y if isinstance(self.__rect, pygame.Rect) else 0
        common = ("center", "topleft", "topright", "bottomleft", "bottomright", "midtop", "midbottom", "midleft", "midright")
        if not any(key in kwargs for key in ("x", "left", "right", "centerx", *common)):
            kwargs["x"] = x
        if not any(key in kwargs for key in ("y", "top", "bottom", "centery", *common)):
            kwargs["y"] = y
        self.__rect = self.image.get_rect(**kwargs)
        self.__former_moves = kwargs.copy()

    def move_ip(self, x: float, y: float) -> None:
        self.__rect = self.image.get_rect(x=self.__rect.x + x, y=self.__rect.y + y)
        self.__former_moves = {"x": self.__rect.x, "y": self.__rect.y}

    @property
    def rotate(self):
        return self.__rotate

    @rotate.setter
    def rotate(self, angle: int) -> None:
        while not 0 <= angle < 360:
            angle += 360 if angle < 0 else -360
        if angle != 0:
            self.image = pygame.transform.rotozoom(self.image, angle, 1)
            self.__rotate += angle

    def set_size(self, *args, smooth=True) -> None:
        size = args if len(args) == 2 else args[0]
        if not isinstance(size, (tuple, list)):
            size = (size, size)
        size = (round(size[0]), round(size[1]))
        if size[0] > 0 and size[1] > 0:
            if smooth:
                self.image = pygame.transform.smoothscale(self.image, size)
            else:
                self.image = pygame.transform.scale(self.image, size)
            self.__valid_size = True
        else:
            self.__valid_size = False

    def set_width(self, width: float, smooth=True)-> None:
        height = 0 if width == 0 else round(self.__rect.h * width / self.__rect.w)
        self.set_size(width, height, smooth=smooth)

    def set_height(self, height: float, smooth=True) -> None:
        width = 0 if height == 0 else round(self.__rect.w * height / self.__rect.h)
        self.set_size(width, height, smooth=smooth)

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

class Focusable:

    MODE_MOUSE = "mouse"
    MODE_KEY = "keyboard"
    MODE_JOY = "joystick"
    MODE = MODE_MOUSE
    ON_LEFT = "on_left"
    ON_RIGHT = "on_right"
    ON_TOP = "on_top"
    ON_BOTTOM = "on_bottom"

    def __init__(self, master, highlight_color=(0, 0, 255), highlight_thickness=2):
        self.__focus = False
        self.__master = master
        self.__side = dict.fromkeys((Focusable.ON_LEFT, Focusable.ON_RIGHT, Focusable.ON_TOP, Focusable.ON_BOTTOM))
        self.__take_focus = True
        master.focus_add(self)
        self.highlight_color = highlight_color
        self.highlight_thickness = highlight_thickness

    def get_obj_on_side(self, side: str):
        return self.__side.get(side, None)

    def set_obj_on_side(self, on_top=None, on_bottom=None, on_left=None, on_right=None) -> None:
        for side, obj in ((Focusable.ON_TOP, on_top), (Focusable.ON_BOTTOM, on_bottom), (Focusable.ON_LEFT, on_left), (Focusable.ON_RIGHT, on_right)):
            if side in self.__side and issubclass(type(obj), Focusable):
                self.__side[side] = obj

    def remove_obj_on_side(self, *sides: str):
        for side in sides:
            if side in self.__side:
                self.__side[side] = None

    def after_drawing(self, surface: pygame.Surface):
        if not self.has_focus() or (hasattr(self, "is_shown") and getattr(self, "is_shown")() is False):
            return
        if hasattr(self, "rect"):
            outline = getattr(self, "outline") if hasattr(self, "outline") else self.highlight_thickness
            if outline <= 0:
                outline = self.highlight_thickness
            if outline > 0:
                pygame.draw.rect(surface, self.highlight_color, getattr(self, "rect"), width=outline)

    def has_focus(self) -> bool:
        return self.__focus

    def take_focus(self, status=None) -> bool:
        if status:
            self.__take_focus = bool(status)
        return self.__take_focus

    def focus_set(self, from_master=False) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            self.__focus = False
        elif not self.has_focus():
            if not from_master and self.take_focus():
                self.__master.set_focus(self)
            self.__focus = True
            if self.take_focus():
                self.on_focus_set()

    def focus_leave(self, remove_from_master=False) -> None:
        if self.has_focus():
            self.__focus = False
            if remove_from_master:
                self.__master.set_focus(None)
            if hasattr(self, "is_shown") and getattr(self, "is_shown")() is True and self.take_focus():
                self.on_focus_leave()

    def focus_update(self):
        pass

    def on_focus_set(self):
        pass

    def on_focus_leave(self):
        pass

class Clickable(Focusable):

    NORMAL = "normal"
    DISABLED = "disabled"

    def __init__(self, master, callback: Optional[Callable[..., Any]] = None,
                 state="normal", hover_sound=None, on_click_sound=None, disabled_sound=None, **kwargs):
        Focusable.__init__(self, master, **kwargs)
        self.__callback = None
        self.__hover = False
        self.__active = False
        self.__hover_sound = None if hover_sound is None else pygame.mixer.Sound(hover_sound)
        self.__on_click_sound = None if on_click_sound is None else pygame.mixer.Sound(on_click_sound)
        self.__disabled_sound = None if disabled_sound is None else pygame.mixer.Sound(disabled_sound)
        self.__enable_mouse = True
        self.__enable_key = True
        self.__state = Clickable.NORMAL
        self.callback = callback
        self.state = state
        master.bind_event(pygame.KEYDOWN, self.event_click_down)
        master.bind_event(pygame.KEYUP, self.event_click_up)
        master.bind_event(pygame.MOUSEBUTTONDOWN, self.event_click_down)
        master.bind_event(pygame.MOUSEBUTTONUP, self.event_click_up)
        master.bind_event(pygame.JOYBUTTONDOWN, self.event_click_down)
        master.bind_event(pygame.JOYBUTTONUP, self.event_click_up)
        master.bind_mouse(self.mouse_motion)

    @property
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self, callback: Callable[..., Any]):
        if callable(callback):
            self.__callback = callback
        else:
            self.__callback = None

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value: str):
        if value not in (Clickable.NORMAL, Clickable.DISABLED):
            return
        self.__state = value
        self.on_change_state()

    @property
    def hover_sound(self):
        return self.__hover_sound

    @property
    def on_click_sound(self):
        return self.__on_click_sound

    @property
    def disabled_sound(self):
        return self.__disabled_sound

    @property
    def active(self):
        return self.__active

    @active.setter
    def active(self, status: bool):
        status = bool(status)
        active = self.__active
        self.__active = status
        if status is True:
            if not active:
                self.on_active_set()
        else:
            if active:
                self.on_active_unset()

    @property
    def hover(self):
        return self.__hover

    @hover.setter
    def hover(self, status: bool):
        status = bool(status)
        hover = self.__hover
        self.__hover = status
        if status is True:
            if not hover:
                self.play_hover_sound()
                self.on_hover()
        else:
            if hover:
                self.on_leave()

    def play_hover_sound(self):
        if isinstance(self.hover_sound, pygame.mixer.Sound):
            self.hover_sound.play()

    def play_on_click_sound(self):
        if self.state == Clickable.NORMAL and isinstance(self.on_click_sound, pygame.mixer.Sound):
            self.on_click_sound.play()
        elif self.state == Clickable.DISABLED and isinstance(self.disabled_sound, pygame.mixer.Sound):
            self.disabled_sound.play()

    def valid_click(self, event: Event, down: bool) -> bool:
        mouse_event = pygame.MOUSEBUTTONDOWN if down else pygame.MOUSEBUTTONUP
        key_event = pygame.KEYDOWN if down else pygame.KEYUP
        joy_event = pygame.JOYBUTTONDOWN if down else pygame.JOYBUTTONUP
        if Focusable.MODE == Focusable.MODE_MOUSE and self.__enable_mouse and hasattr(self, "rect"):
            if event.type == mouse_event and event.button == 1 and getattr(self, "rect").collidepoint(event.pos):
                return True
        elif Focusable.MODE in [Focusable.MODE_KEY, Focusable.MODE_JOY] and self.__enable_key and self.take_focus() and self.has_focus():
            if event.type == key_event and event.key == pygame.K_RETURN:
                return True
            if event.type == joy_event and event.button == 0:
                return True
        return False

    def event_click_up(self, event: Event) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            return
        if not self.active:
            return
        self.active = False
        self.on_click_up(event)
        if self.valid_click(event, down=False):
            self.play_on_click_sound()
            self.on_hover()
            if self.__callback  and self.state != Clickable.DISABLED:
                self.__callback()

    def event_click_down(self, event: Event) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            return
        if self.valid_click(event, down=True):
            self.active = True
            self.on_click_down(event)

    def mouse_motion(self, mouse_pos: Tuple[int, int]) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            return
        if Focusable.MODE == Focusable.MODE_MOUSE and self.__enable_mouse:
            if hasattr(self, "rect"):
                self.hover = getattr(self, "rect").collidepoint(mouse_pos)
                self.on_mouse_motion(mouse_pos)
            else:
                self.hover = False

    def enable_mouse(self):
        self.__enable_mouse = True

    def disable_mouse(self):
        self.__enable_mouse = False

    def enable_key_joy(self):
        self.__enable_key = True

    def disable_key_joy(self):
        self.__enable_key = False

    def focus_update(self):
        if Focusable.MODE != Focusable.MODE_MOUSE and self.take_focus():
            self.hover = self.has_focus()
        elif Focusable.MODE == Focusable.MODE_MOUSE:
            if self.hover:
                self.focus_set()
            else:
                self.focus_leave(remove_from_master=True)

    def on_change_state(self) -> None:
        pass

    def on_click_down(self, event: Event) -> None:
        pass

    def on_click_up(self, event: Event) -> None:
        pass

    def on_mouse_motion(self, mouse_pos: Tuple[int, int]) -> None:
        pass

    def on_hover(self) -> None:
        pass

    def on_leave(self) -> None:
        pass

    def on_active_set(self) -> None:
        pass

    def on_active_unset(self) -> None:
        pass