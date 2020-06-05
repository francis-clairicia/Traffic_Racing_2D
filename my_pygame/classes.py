# -*- coding: Utf-8 -*

from typing import Tuple, Optional, Any, Union, List, Callable
import pygame
from pygame.font import Font, SysFont
from pygame.sprite import Sprite, Group

class Drawable(Sprite):
    def __init__(self, surface: Optional[pygame.Surface] = pygame.Surface((0, 0), flags=pygame.SRCALPHA),
                 rotate: Optional[int] = 0, groups: Optional[Union[List[Group], Tuple[Group, ...]]] = tuple(), **kwargs):
        Sprite.__init__(self, *groups)
        self.__sounds = list()
        self.former_moves = dict()
        self.image = surface
        self.draw_sprite = True
        self.valid_size = True
        self.rotate(rotate)
        self.move(**kwargs)

    def __setattr__(self, name: str, value: Any):
        if isinstance(value, pygame.mixer.Sound):
            self.__sounds.append(value)
        elif issubclass(type(value), Drawable):
            self.__sounds.extend(value.sounds)
        return object.__setattr__(self, name, value)

    def fill(self, color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> None:
        self.image.fill(color)
        self.mask = pygame.mask.from_surface(self.image)

    def blit(self, surface, dest) -> pygame.Rect:
        rect = self.image.blit(surface, dest)
        self.mask = pygame.mask.from_surface(self.image)
        return rect

    def show(self) -> None:
        self.draw_sprite = True

    def hide(self) -> None:
        self.draw_sprite = False

    def is_shown(self) -> bool:
        return bool(self.draw_sprite and self.valid_size)

    @property
    def image(self) -> pygame.Surface:
        return self.__surface

    @image.setter
    def image(self, surface: pygame.Surface) -> None:
        self.__surface = surface
        self.rect = self.__surface.get_rect()
        self.mask = pygame.mask.from_surface(self.__surface)
        self.move(**self.former_moves)

    @property
    def sounds(self) -> Tuple[pygame.mixer.Sound, ...]:
        return tuple(self.__sounds)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            surface.blit(self.image, self.rect)

    def move(self, **kwargs) -> None:
        x = self.rect.x if hasattr(self, "rect") else 0
        y = self.rect.y if hasattr(self, "rect") else 0
        self.rect = self.image.get_rect(**kwargs)
        common = ["center", "topleft", "topright", "bottomleft", "bottomright", "midtop", "midbottom", "midleft", "midright"]
        if not any(key in kwargs for key in ["x", "left", "right", "centerx", *common]):
            self.rect.x = x
            kwargs["x"] = x
        if not any(key in kwargs for key in ["y", "top", "bottom", "centery", *common]):
            self.rect.y = y
            kwargs["y"] = y
        self.former_moves = kwargs.copy()

    def move_ip(self, x: float, y: float) -> None:
        self.rect.move_ip(x, y)

    def rotate(self, angle: int) -> None:
        while not 0 <= angle < 360:
            angle += 360 if angle < 0 else -360
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)

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
            self.valid_size = True
        else:
            self.valid_size = False

    def set_width(self, width: float, smooth=True)-> None:
        height = 0 if width == 0 else round(self.rect.h * width / self.rect.w)
        self.set_size(width, height, smooth=smooth)

    def set_height(self, height: float, smooth=True) -> None:
        width = 0 if height == 0 else round(self.rect.w * height / self.rect.h)
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
        self.master = master
        self.highlight_color = highlight_color
        self.highlight_thickness = highlight_thickness
        self.default_outline = None
        self.default_outline_color = None
        self.highlight = False
        self.__side = {key: None for key in (Focusable.ON_LEFT, Focusable.ON_RIGHT, Focusable.ON_TOP, Focusable.ON_BOTTOM)}

    def get_obj_on_side(self, side: str):
        return self.__side.get(side, None)

    def set_obj_on_side(self, on_top=None, on_bottom=None, on_left=None, on_right=None) -> None:
        for side, obj in ((Focusable.ON_TOP, on_top), (Focusable.ON_BOTTOM, on_bottom), (Focusable.ON_LEFT, on_left), (Focusable.ON_RIGHT, on_right)):
            if side in self.__side and issubclass(type(obj), Focusable):
                self.__side[side] = obj

    def remove_obj_on_side(self, side: str):
        if side in self.__side:
            self.__side[side] = None

    def after_drawing(self, surface: pygame.Surface):
        if not self.has_focus():
            return
        if hasattr(self, "rect"):
            outline = getattr(self, "outline") if hasattr(self, "outline") else self.highlight_thickness
            if outline <= 0:
                outline = self.highlight_thickness
            if outline <= 0:
                return
            pygame.draw.rect(surface, self.highlight_color, getattr(self, "rect"), width=outline)

    def has_focus(self) -> bool:
        return self.__focus

    def focus_set(self, from_master=False) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            self.__focus = False
        elif not self.has_focus():
            if not from_master:
                self.master.set_focus(self)
            self.__focus = True
            self.on_focus_set()

    def focus_leave(self) -> None:
        if self.has_focus():
            self.__focus = False
            if hasattr(self, "is_shown") and getattr(self, "is_shown")() is True:
                self.on_focus_leave()

    def on_focus_set(self):
        pass

    def on_focus_leave(self):
        pass

class Clickable(Focusable):
    def __init__(self, master, callback: Optional[Callable[..., Any]] = None, hover_sound=None, on_click_sound=None, **kwargs):
        Focusable.__init__(self, master, **kwargs)
        self.__hover = False
        self.__active = False
        self.callback = callback
        self.hover_sound = None if hover_sound is None else pygame.mixer.Sound(hover_sound)
        self.on_click_sound = None if on_click_sound is None else pygame.mixer.Sound(on_click_sound)
        master.bind_event(pygame.KEYDOWN, self.click_down)
        master.bind_event(pygame.KEYUP, self.click_up)
        master.bind_event(pygame.MOUSEBUTTONDOWN, self.click_down)
        master.bind_event(pygame.MOUSEBUTTONUP, self.click_up)
        master.bind_event(pygame.JOYBUTTONDOWN, self.click_down)
        master.bind_event(pygame.JOYBUTTONUP, self.click_up)
        master.bind_mouse(self.mouse_motion)

    @property
    def active(self):
        return self.__active

    @active.setter
    def active(self, status: bool):
        status = bool(status)
        if status is True:
            if not self.__active:
                self.on_active()
        self.__active = status

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
                if isinstance(self.hover_sound, pygame.mixer.Sound):
                    self.hover_sound.play()
                self.on_hover()
        else:
            if hover:
                self.on_leave()

    def valid_click(self, event: pygame.event.Event, down: bool) -> bool:
        mouse_event = pygame.MOUSEBUTTONDOWN if down else pygame.MOUSEBUTTONUP
        key_event = pygame.KEYDOWN if down else pygame.KEYUP
        joy_event = pygame.JOYBUTTONDOWN if down else pygame.JOYBUTTONUP
        if Focusable.MODE == Focusable.MODE_MOUSE and hasattr(self, "rect"):
            if event.type == mouse_event and event.button == 1 and getattr(self, "rect").collidepoint(event.pos):
                return True
        elif Focusable.MODE in [Focusable.MODE_KEY, Focusable.MODE_JOY] and self.has_focus():
            if event.type == key_event and event.key == pygame.K_RETURN:
                return True
            if event.type == joy_event and event.button == 0:
                return True
        return False

    def click_up(self, event: pygame.event.Event) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            return
        if not self.active:
            return
        self.active = False
        self.on_click_up(event)
        if self.valid_click(event, down=False):
            if isinstance(self.on_click_sound, pygame.mixer.Sound):
                self.on_click_sound.play()
            self.on_hover()
            if self.callback is not None:
                self.callback()

    def click_down(self, event: pygame.event.Event) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            return
        if self.valid_click(event, down=True):
            self.active = True
            self.on_click_down(event)

    def mouse_motion(self, mouse_pos: Tuple[int, int]) -> None:
        if hasattr(self, "is_shown") and getattr(self, "is_shown")() is False:
            return
        if Focusable.MODE in [Focusable.MODE_KEY, Focusable.MODE_JOY]:
            self.hover = self.has_focus()
        elif Focusable.MODE == Focusable.MODE_MOUSE:
            if hasattr(self, "rect"):
                self.hover = getattr(self, "rect").collidepoint(mouse_pos)
            else:
                self.hover = False
            self.on_mouse_motion(mouse_pos)
        else:
            self.hover = False

    def on_click_down(self, event: pygame.event.Event) -> None:
        pass

    def on_click_up(self, event: pygame.event.Event) -> None:
        pass

    def on_mouse_motion(self, mouse_pos: Tuple[int, int]) -> None:
        pass

    def on_hover(self) -> None:
        pass

    def on_leave(self) -> None:
        pass

    def on_active(self) -> None:
        pass

class Image(Drawable):
    def __init__(self, filepath: str, size=None, width=None, height=None, **kwargs):
        Drawable.__init__(self, pygame.image.load(filepath).convert_alpha(), **kwargs)
        if size is not None:
            self.set_size(size)
        elif width is not None and height is not None:
            self.set_size(width, height)
        elif width is not None:
            self.set_width(width)
        elif height is not None:
            self.set_height(height)

class Text(Drawable):

    T_LEFT = "left"
    T_RIGHT = "right"
    T_CENTER = "center"

    def __init__(self, text: str, font: Union[Font, SysFont, Tuple[int, str, str]], color: tuple, justify="left", **kwargs):
        Drawable.__init__(self, **kwargs)
        if font is None:
            font = SysFont(pygame.font.get_default_font(), 15)
        self.color = color
        self.justify = justify
        self.font = font
        self.string = text
        self.refresh()

    @property
    def font(self) -> Font:
        return self.__font

    @font.setter
    def font(self, font: Union[Font, SysFont, Tuple[int, str, str]]) -> None:
        if isinstance(font, (tuple, list)):
            if str(font[0]).endswith((".ttf", ".otf")):
                self.__font = Font(*font[0:2])
                if "bold" in font:
                    self.__font.set_bold(True)
                if "italic" in font:
                    self.__font.set_italic(True)
            else:
                self.__font = SysFont(*font[0:2], bold=bool("bold" in font), italic=bool("italic" in font))
            if "underline" in font:
                self.__font.set_underline(True)
        else:
            self.__font = font
        self.refresh()

    @property
    def string(self) -> str:
        return self.__str

    @string.setter
    def string(self, string: str) -> None:
        self.__str = str(string)
        self.refresh()

    def refresh(self) -> None:
        if not hasattr(self, "string") or not hasattr(self, "font"):
            return
        render_lines = list()
        for line in self.string.splitlines():
            render = self.font.render(line, True, self.color)
            render_lines.append(render)
        if len(render_lines) > 0:
            size = (
                max(render.get_width() for render in render_lines),
                sum(render.get_height() for render in render_lines)
            )
            self.image = pygame.Surface(size, flags=pygame.SRCALPHA)
            self.fill((0, 0, 0, 0))
            y = 0
            justify_parameters = {
                Text.T_LEFT:    {"left": 0},
                Text.T_RIGHT:   {"right": size[0]},
                Text.T_CENTER:  {"centerx": size[0] // 2},
            }
            params = justify_parameters.get(self.justify, dict())
            for render in render_lines:
                self.blit(render, render.get_rect(**params, y=y))
                y += render.get_height()
        else:
            self.image = pygame.Surface((0, 0), flags=pygame.SRCALPHA)

    def set_color(self, color: tuple) -> None:
        self.color = tuple(color)
        self.refresh()

class RectangleShape(Drawable):
    def __init__(self, width: int, height: int, color: tuple, outline=0, outline_color=(0, 0, 0), **kwargs):
        Drawable.__init__(self, pygame.Surface((int(width), int(height)), flags=pygame.SRCALPHA), **kwargs)
        self.color = color
        self.outline = outline
        self.outline_color = outline_color

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            Drawable.draw(self, surface)
            if self.outline > 0:
                pygame.draw.rect(surface, self.outline_color, self.rect, self.outline)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value: tuple):
        self.fill(value)
        self.__color = value


class Button(RectangleShape, Clickable):
    def __init__(self, master, text: str, font=None, command: Optional[Callable[..., Any]] = None,
                 bg=(255, 255, 255), fg=(0, 0, 0),
                 outline=2, outline_color=(0, 0, 0),
                 hover_bg=(235, 235, 235), hover_fg=None, hover_sound=None,
                 active_bg=(128, 128, 128), active_fg=None, on_click_sound=None,
                 highlight_color=(0, 0, 255),
                 **kwargs):
        RectangleShape.__init__(self, width=1, height=1, color=bg, outline=outline, outline_color=outline_color, **kwargs)
        Clickable.__init__(self, master, command, hover_sound=hover_sound, on_click_sound=on_click_sound, highlight_color=highlight_color)
        self.text = Text(text, font, fg, justify=Text.T_CENTER)
        self.set_size(self.text.w + 20, self.text.h + 20, smooth=False)
        self.fg = fg
        self.bg = bg
        self.hover_fg = fg if hover_fg is None else hover_fg
        self.hover_bg = bg if hover_bg is None else hover_bg
        self.active_fg = fg if active_fg is None else active_fg
        self.active_bg = bg if active_bg is None else active_bg

    def set_text(self, string: str) -> None:
        self.text.string = string
        w, h = (self.text.w + 20, self.text.h + 20)
        self.set_size(w, h)

    def get_text(self) -> str:
        return self.text.string

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            RectangleShape.draw(self, surface)
            self.text.move(center=self.center)
            self.text.draw(surface)

    def on_hover(self) -> None:
        self.color = self.hover_bg if not self.active else self.active_bg
        self.text.set_color(self.hover_fg if not self.active else self.active_fg)

    def on_leave(self) -> None:
        self.color = self.bg
        self.text.set_color(self.fg)

    def on_active(self) -> None:
        self.color = self.active_bg
        self.text.set_color(self.active_fg)

    def on_focus_set(self) -> None:
        self.hover = True

    def on_focus_leave(self) -> None:
        self.hover = False

class ImageButton(Button):

    def __init__(self, master, image: Image, hover_img: Optional[Image] = None, active_img: Optional[Image] = None, show_bg=False, offset=3, **kwargs):
        Button.__init__(self, master, str(), **kwargs)
        self.image_button = image
        self.default_img = image
        self.hover_img = hover_img
        self.active_img = active_img
        self.show_background(show_bg)
        self.set_size(self.image_button.w + 20, self.image_button.h + 20)
        self.__offset = offset
        self.offset = 0

    def show_background(self, status: bool) -> None:
        self._show = bool(status)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            if self._show:
                RectangleShape.draw(self, surface)
            self.image_button.move(center=self.center)
            self.image_button.move_ip(0, self.offset)
            self.image_button.draw(surface)

    def on_hover(self):
        if self._show:
            Button.on_hover(self)
        if self.active_img is not None and self.active:
            self.image_button = self.active_img
        elif self.hover_img is not None and self.hover:
            self.image_button = self.hover_img
        else:
            self.image_button = self.default_img

    def on_click_up(self, event: pygame.event.Event):
        if self._show:
            Button.on_click_up(self, event)
        self.image_button = self.default_img
        self.offset = 0

    def on_click_down(self, event):
        if self._show:
            Button.on_click_down(self, event)
        if self.active_img is not None:
            self.image_button = self.active_img
        self.offset = self.__offset

class TextButton(Button):
    def __init__(self, master, text: str, color: tuple, font, outline=0, shadow=(0, 0, 0), offset=3, **kwargs):
        kwargs["bg"] = kwargs["hover_bg"] = kwargs["active_bg"] = (0, 0, 0, 0)
        kwargs["fg"] = color
        Button.__init__(self, master, text, font=font, outline=outline, **kwargs)
        self.shadow = shadow
        self.__offset = offset
        self.offset = 0

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            RectangleShape.draw(self, surface)
            self.text.move(center=self.center)
            if self.offset != self.__offset:
                color = tuple(self.text.color)
                self.text.set_color(self.shadow)
                self.text.move_ip(0, self.__offset)
                self.text.draw(surface)
                self.text.set_color(color)
                self.text.move(center=self.center)
            self.text.move_ip(0, self.offset)
            self.text.draw(surface)

    def on_click_up(self, event):
        self.offset = 0

    def on_click_down(self, event):
        self.offset = self.__offset

class Entry(RectangleShape, Clickable):
    def __init__(self, master, font=None, width=10, bg=(255, 255, 255), fg=(0, 0, 0),
                 highlight_color=(128, 128, 128), **kwargs):
        self.text = Text("".join("1" for _ in range(width)), font, fg)
        size = (self.text.w + 20, self.text.h + 20)
        RectangleShape.__init__(self, size, bg, **kwargs)
        Clickable.__init__(self, master, highlight_color=highlight_color)
        self.text.string = ""
        self.nb_chars = width
        master.bind_event(pygame.MOUSEBUTTONUP, self.focus_set)
        master.bind_event(pygame.KEYDOWN, self.key_press)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            RectangleShape.draw(self, surface)
            self.text.move(left=self.left + 10, centery=self.centery)
            self.text.draw(surface)
            if self.has_focus():
                cursor_start = (self.text.right + 2, self.text.top)
                cursor_end = (self.text.right + 2, self.text.bottom)
                pygame.draw.line(surface, self.text.color, cursor_start, cursor_end, 2)

    def get(self) -> str:
        return self.text.string

    def key_press(self, event: pygame.event.Event) -> None:
        if not self.has_focus():
            return
        if event.key == pygame.K_BACKSPACE:
            self.text.string = self.text.string[:-1]
        elif len(self.text.string) < self.nb_chars:
            self.text.string += event.unicode


class Scale(RectangleShape, Clickable):

    S_TOP = "top"
    S_BOTTOM = "bottom"
    S_LEFT = "left"
    S_RIGHT = "right"
    S_INSIDE = "inside"

    def __init__(self, master, width: int, height: int, color: tuple, scale_color: tuple,
                 from_=0, to=1, default=None, command=None,
                 highlight_color=(0, 0, 255), hover_sound=None, on_click_sound=None, **kwargs):
        RectangleShape.__init__(self, width, height, (0, 0, 0, 0), **kwargs)
        Clickable.__init__(self, master, command, highlight_color=highlight_color, hover_sound=hover_sound, on_click_sound=on_click_sound)
        if to <= from_:
            raise ValueError("end value 'to' must be greather than 'from'")
        self.__start = from_
        self.__end = to
        self.percent = 0
        if default is not None:
            self.value = default
        kwargs.pop("outline", None)
        self.scale_rect = RectangleShape(width, height, scale_color, **kwargs)
        self.bg_rect = RectangleShape(width, height, color, **kwargs)
        self.__show_value_params = dict()
        self.__show_label_params = dict()
        master.bind_joystick_axis(0, "AXIS_LEFT_X", self.axis_event)

    def set_size(self, *args, smooth=True):
        RectangleShape.set_size(self, *args, smooth=smooth)
        self.scale_rect.set_size(*args, smooth=smooth)
        self.bg_rect.set_size(*args, smooth=smooth)

    def draw(self, surface: pygame.Surface) -> None:
        self.call_update()
        if self.is_shown():
            self.scale_rect.set_size(self.width * self.percent, self.height, smooth=False)
            self.bg_rect.move(x=self.x, centery=self.centery)
            self.scale_rect.move(x=self.x, centery=self.centery)
            self.bg_rect.draw(surface)
            self.scale_rect.draw(surface)
            RectangleShape.draw(self, surface)
            if len(self.__show_value_params) > 0:
                font = self.__show_value_params["font"]
                color = self.__show_value_params["color"]
                movements = self.__show_value_params["movements"]
                round_n = self.__show_value_params["round"]
                value = round(self.value, round_n) if round_n != 0 else round(self.value)
                Text(value, font, color, **movements).draw(surface)
            if len(self.__show_label_params) > 0:
                label = self.__show_label_params["label"]
                font = self.__show_label_params["font"]
                color = self.__show_label_params["color"]
                movements = self.__show_label_params["movements"]
                Text(label, font, color, **movements).draw(surface)

    def show_value(self, font, color, side, round_n=0):
        offset = 10
        movements = {
            Scale.S_TOP:    {"bottom": self.top - offset, "centerx": self.centerx},
            Scale.S_BOTTOM: {"top": self.bottom + offset, "centerx": self.centerx},
            Scale.S_LEFT:   {"right": self.left - offset, "centery": self.centery},
            Scale.S_RIGHT:  {"left": self.right + offset, "centery": self.centery},
            Scale.S_INSIDE: {"center": self.center}
        }
        if side not in movements:
            return
        self.__show_value_params.update(font=font, color=color, movements=movements[side], round=round_n)

    def show_label(self, label, font, color, side):
        offset = 10
        movements = {
            Scale.S_TOP:    {"bottom": self.top - offset, "centerx": self.centerx},
            Scale.S_BOTTOM: {"top": self.bottom + offset, "centerx": self.centerx},
            Scale.S_LEFT:   {"right": self.left - offset, "centery": self.centery},
            Scale.S_RIGHT:  {"left": self.right + offset, "centery": self.centery},
        }
        if side not in movements:
            return
        self.__show_label_params.update(label=label, font=font, color=color, movements=movements[side])

    def mouse_move_event(self, mouse_pos):
        if self.active:
            self.percent = (mouse_pos[0] - self.x) / self.width

    def axis_event(self, value):
        if self.has_focus() and self.active:
            self.percent += (0.01 * value)

    def on_click_down(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_move_event(event.pos)

    def on_mouse_motion(self, mouse_pos: Tuple[int, int]) -> None:
        self.mouse_move_event(mouse_pos)

    def call_update(self):
        if hasattr(self, "callback") and self.callback is not None:
            self.callback()

    @property
    def percent(self):
        return self.__percent

    @percent.setter
    def percent(self, value: float):
        if value > 1:
            value = 1
        elif value < 0:
            value = 0
        self.__percent = value
        self.__value = self.__start + (self.__percent * self.__end)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: float):
        if value > self.__end:
            value = self.__end
        elif value < self.__start:
            value = self.__start
        self.__value = value
        self.__percent = (self.__value - self.__start) / (self.__end - self.__start)

class CheckBox(RectangleShape, Clickable):
    def __init__(self, master, width: int, height: int, color: tuple, state=False, outline=2,
                 image: Optional[Image] = None, command: Optional[Callable[..., Any]] = None,
                 highlight_color=(0, 0, 255), hover_sound=None, on_click_sound=None, **kwargs):
        RectangleShape.__init__(self, width, height, color, outline=outline, **kwargs)
        Clickable.__init__(self, master, self.change_state, highlight_color=highlight_color, hover_sound=hover_sound, on_click_sound=on_click_sound)
        self.__on_changed_state = command
        self.active_img = image
        self.state = state

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value: bool):
        self.__state = bool(value)
        if self.__on_changed_state is not None:
            self.__on_changed_state(self.__state)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            RectangleShape.draw(self, surface)
            if self.state is True:
                if isinstance(self.active_img, Image):
                    self.active_img.center = self.center
                    self.active_img.draw(surface)
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
    def change_state(self):
        self.state = not self.state