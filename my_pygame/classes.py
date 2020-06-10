# -*- coding: Utf-8 -*

from typing import Tuple, Optional, Any, Union, Callable
import pygame
from pygame.event import Event
from pygame.font import Font, SysFont
from .abstract import Drawable, Clickable

class Image(Drawable):
    def __init__(self, filepath: str, size=None, width=None, height=None, **kwargs):
        Drawable.__init__(self, pygame.image.load(filepath).convert_alpha(), **kwargs)
        self.__filepath = filepath
        if size is not None:
            self.set_size(size)
        elif width is not None and height is not None:
            if self.width > width:
                self.set_width(width)
            if self.height > height:
                self.set_height(height)
        elif width is not None:
            self.set_width(width)
        elif height is not None:
            self.set_height(height)

    @property
    def filepath(self):
        return self.__filepath

    def load(self, filepath: str, keep_width=False, keep_height=False) -> None:
        if keep_width or keep_height:
            width, height = self.size
        self.image = pygame.image.load(filepath).convert_alpha()
        self.__filepath = filepath
        if keep_width and keep_height:
            self.set_size(width, height)
        elif keep_width:
            self.set_width(width)
        elif keep_height:
            self.set_height(height)

    def copy(self):
        return Image(self.filepath, size=self.size, rotate=self.rotate)

class Text(Drawable):

    T_LEFT = "left"
    T_RIGHT = "right"
    T_CENTER = "center"

    def __init__(self, text: str, font: Union[Font, SysFont, Tuple[int, str, str]], color=(0, 0, 0),
                 justify="left", shadow_x=0, shadow_y=0, shadow_color=(0, 0, 0),
                 img=None, compound="left", **kwargs):
        Drawable.__init__(self, **kwargs)
        if font is None:
            font = SysFont(pygame.font.get_default_font(), 15)
        self.color = color
        self.justify = justify
        self.font = font
        self.string = text
        self.img = img
        self.compound = compound
        self.shadow = (shadow_x, shadow_y)
        self.shadow_color = shadow_color

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

    @property
    def img(self):
        return self.__img

    @img.setter
    def img(self, img):
        self.__img = img
        self.refresh()

    @property
    def compound(self):
        return self.__compound

    @compound.setter
    def compound(self, value: str):
        if value not in ("left", "right", "top", "bottom", "center"):
            return
        self.__compound = value
        self.refresh()

    def set_string(self, string: str) -> None:
        self.string = string

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown() and any(value != 0 for value in self.shadow[0:2]):
            shadow = Text(self.string, self.font, self.shadow_color, center=self.center, justify=self.justify)
            shadow.move_ip(*self.shadow)
            shadow.draw(surface)
        Drawable.draw(self, surface)

    def refresh(self) -> None:
        if any(not hasattr(self, attr) for attr in ("string", "font", "img", "compound")):
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
            text = pygame.Surface(size, flags=pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            y = 0
            justify_parameters = {
                Text.T_LEFT:    {"left": 0},
                Text.T_RIGHT:   {"right": size[0]},
                Text.T_CENTER:  {"centerx": size[0] // 2},
            }
            params = justify_parameters.get(self.justify, dict())
            for render in render_lines:
                text.blit(render, render.get_rect(**params, y=y))
                y += render.get_height()
        else:
            text = pygame.Surface((0, 0), flags=pygame.SRCALPHA)
        if isinstance(self.img, Image):
            function_to_get_size = {
                "left": {"width": sum, "height": max},
                "right": {"width": sum, "height": max},
                "top": {"width": max, "height": sum},
                "bottom": {"width": max, "height": sum},
                "center": {"width": max, "height": max},
            }
            size = {"width": 0, "height": 0}
            for field in size:
                size[field] = function_to_get_size[self.compound][field](getattr(obj, field) for obj in [text.get_rect(), self.img])
            w = size["width"] + 5
            h = size["height"]
            self.image = pygame.Surface((w, h), flags=pygame.SRCALPHA)
            rect_to_draw = self.image.get_rect()
            move_text = {
                "left": {"right": rect_to_draw.right, "centery": rect_to_draw.centery},
                "right": {"left": rect_to_draw.left, "centery": rect_to_draw.centery},
                "top": {"bottom": rect_to_draw.bottom, "centerx": rect_to_draw.centerx},
                "bottom": {"top": rect_to_draw.bottom, "centerx": rect_to_draw.centerx},
                "center": {"center": rect_to_draw.center}
            }
            move_img = {
                "left": {"left": rect_to_draw.left, "centery": rect_to_draw.centery},
                "right": {"right": rect_to_draw.right, "centery": rect_to_draw.centery},
                "top": {"top": rect_to_draw.bottom, "centerx": rect_to_draw.centerx},
                "bottom": {"bottom": rect_to_draw.bottom, "centerx": rect_to_draw.centerx},
                "center": {"center": rect_to_draw.center}
            }
            self.image.blit(text, text.get_rect(**move_text[self.compound]))
            self.img.move(**move_img[self.compound])
            self.img.draw(self.image)
        else:
            self.image = text

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
        self.image.fill(value)
        self.__color = value


class Button(RectangleShape, Clickable):
    def __init__(self, master, text: str, font=None, img=None, compound="left",
                 command: Optional[Callable[..., Any]] = None, state="normal",
                 bg=(255, 255, 255), fg=(0, 0, 0),
                 outline=2, outline_color=(0, 0, 0),
                 hover_bg=(235, 235, 235), hover_fg=None, hover_sound=None,
                 active_bg=(128, 128, 128), active_fg=None, on_click_sound=None,
                 disabled_bg=(128, 128, 128), disabled_fg=None, disabled_sound=None,
                 highlight_color=(0, 0, 255),
                 **kwargs):
        RectangleShape.__init__(self, width=1, height=1, color=bg, outline=outline, outline_color=outline_color, **kwargs)
        self.text = Text(text, font, fg, justify=Text.T_CENTER, img=img, compound=compound)
        self.set_size(self.text.w + 20, self.text.h + 20)
        self.fg = fg
        self.bg = bg
        self.hover_fg = fg if hover_fg is None else hover_fg
        self.hover_bg = bg if hover_bg is None else hover_bg
        self.active_fg = fg if active_fg is None else active_fg
        self.active_bg = bg if active_bg is None else active_bg
        self.disabled_fg = fg if disabled_fg is None else disabled_fg
        self.disabled_bg = bg if disabled_bg is None else disabled_bg
        Clickable.__init__(self, master, command, state, hover_sound, on_click_sound, disabled_sound, highlight_color=highlight_color)

    def set_text(self, string: str) -> None:
        self.text.string = string
        self.set_size(self.text.w + 20, self.text.h + 20)

    def get_text(self) -> str:
        return self.text.string

    def set_font(self, font) -> None:
        self.text.font = font
        self.set_size(self.text.w + 20, self.text.h + 20)

    def get_font(self) -> Font:
        return self.text.font

    @property
    def img(self):
        return self.text.img

    @img.setter
    def img(self, img: Image):
        self.text.img = img
        self.set_size(self.text.w + 20, self.text.h + 20)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            RectangleShape.draw(self, surface)
            self.text.move(center=self.center)
            self.text.draw(surface)

    def on_hover(self) -> None:
        if self.state == Clickable.DISABLED:
            bg = self.disabled_bg
            fg = self.disabled_fg
        else:
            bg = self.hover_bg if not self.active else self.active_bg
            fg = self.hover_fg if not self.active else self.active_fg
        self.color = bg
        self.text.set_color(fg)

    def on_leave(self) -> None:
        self.set_default_colors()

    def on_change_state(self) -> None:
        if self.hover:
            self.on_hover()
        elif self.active:
            self.on_active_set()
        else:
            self.set_default_colors()

    def set_default_colors(self):
        if self.state == Clickable.DISABLED:
            bg = self.disabled_bg
            fg = self.disabled_fg
        else:
            bg = self.bg
            fg = self.fg
        self.color = bg
        self.text.set_color(fg)

    def on_active_set(self) -> None:
        if self.state == Clickable.DISABLED:
            bg = self.disabled_bg
            fg = self.disabled_fg
        else:
            bg = self.active_bg
            fg = self.active_fg
        self.color = bg
        self.text.set_color(fg)

class ImageButton(Button):

    def __init__(self, master, image: Image, hover_img: Optional[Image] = None, active_img: Optional[Image] = None, show_bg=False, offset=3, **kwargs):
        Button.__init__(self, master, str(), img=image, compound="center", **kwargs)
        self.default_img = self.img
        self.hover_img = hover_img
        self.active_img = active_img
        self.show_background(show_bg)
        self.__offset = offset
        self.offset = 0

    def show_background(self, status: bool) -> None:
        self._show = bool(status)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            if self._show:
                RectangleShape.draw(self, surface)
            self.img.move(center=self.center)
            self.img.move_ip(0, self.offset)
            self.img.draw(surface)

    def on_hover(self):
        Button.on_hover(self)
        if self.active_img is not None and self.active:
            self.img = self.active_img
        elif self.hover_img is not None and self.hover:
            self.img = self.hover_img
        else:
            self.img = self.default_img

    def on_active_set(self):
        Button.on_active_set(self)
        if self.active_img is not None:
            self.img = self.active_img
        self.offset = self.__offset

    def on_active_unset(self):
        if self._show:
            Button.on_active_unset(self)
        self.img = self.default_img
        self.offset = 0

class TextButton(Button):
    def __init__(self, master, text: str, font, color=(0, 0, 0), outline=0, shadow=(0, 0, 0), offset=3, **kwargs):
        kwargs["bg"] = kwargs["hover_bg"] = kwargs["active_bg"] = (0, 0, 0, 0)
        kwargs["fg"] = color
        kwargs["img"] = None
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
                 state="normal", highlight_color=(128, 128, 128), **kwargs):
        self.text = Text("".join("1" for _ in range(width)), font, fg)
        size = (self.text.w + 20, self.text.h + 20)
        RectangleShape.__init__(self, size, bg, **kwargs)
        Clickable.__init__(self, master, state=state, highlight_color=highlight_color)
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

    def key_press(self, event: Event) -> None:
        if not self.has_focus():
            return
        if event.key == pygame.K_BACKSPACE:
            self.text.string = self.text.string[:-1]
        elif len(self.text.string) < self.nb_chars:
            self.text.string += event.unicode

class ProgressBar(RectangleShape):

    S_TOP = "top"
    S_BOTTOM = "bottom"
    S_LEFT = "left"
    S_RIGHT = "right"
    S_INSIDE = "inside"

    def __init__(self, width: int, height: int, color: tuple, scale_color: tuple, outline=2, from_=0, to=1, default=None, **kwargs):
        RectangleShape.__init__(self, width, height, (0, 0, 0, 0), outline=outline, **kwargs)
        if to <= from_:
            raise ValueError("end value 'to' must be greather than 'from'")
        self.__start = from_
        self.__end = to
        self.percent = 0
        if default is not None:
            self.value = default
        self.scale_rect = RectangleShape(width, height, scale_color, **kwargs)
        self.bg_rect = RectangleShape(width, height, color, **kwargs)
        self.__show_value_params = dict()
        self.__show_label_params = dict()

    def set_size(self, *args, smooth=True):
        RectangleShape.set_size(self, *args, smooth=smooth)
        self.scale_rect.set_size(*args, smooth=smooth)
        self.bg_rect.set_size(*args, smooth=smooth)

    def draw(self, surface: pygame.Surface) -> None:
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
                value = round(self.value, round_n) if round_n > 0 else round(self.value)
                Text(value, font, color, **movements).draw(surface)
            if len(self.__show_label_params) > 0:
                label = self.__show_label_params["label"]
                font = self.__show_label_params["font"]
                color = self.__show_label_params["color"]
                movements = self.__show_label_params["movements"]
                Text(label, font, color, **movements).draw(surface)

    def show_value(self, side, font=None, color=(0, 0, 0), round_n=0):
        offset = 10
        movements = {
            ProgressBar.S_TOP:    {"bottom": self.top - offset, "centerx": self.centerx},
            ProgressBar.S_BOTTOM: {"top": self.bottom + offset, "centerx": self.centerx},
            ProgressBar.S_LEFT:   {"right": self.left - offset, "centery": self.centery},
            ProgressBar.S_RIGHT:  {"left": self.right + offset, "centery": self.centery},
            ProgressBar.S_INSIDE: {"center": self.center}
        }
        if side not in movements:
            return
        self.__show_value_params.update(font=font, color=color, movements=movements[side], round=round_n)

    def show_label(self, label, side, font=None, color=(0, 0, 0)):
        offset = 10
        movements = {
            ProgressBar.S_TOP:    {"bottom": self.top - offset, "centerx": self.centerx},
            ProgressBar.S_BOTTOM: {"top": self.bottom + offset, "centerx": self.centerx},
            ProgressBar.S_LEFT:   {"right": self.left - offset, "centery": self.centery},
            ProgressBar.S_RIGHT:  {"left": self.right + offset, "centery": self.centery},
        }
        if side not in movements:
            return
        self.__show_label_params.update(label=label, font=font, color=color, movements=movements[side])

    @property
    def percent(self) -> float:
        return float(self.__percent)

    @percent.setter
    def percent(self, value: float):
        if value > 1:
            value = 1
        elif value < 0:
            value = 0
        self.__percent = value
        self.__value = self.__start + (self.__percent * self.__end)

    @property
    def value(self) -> float:
        return float(self.__value)

    @value.setter
    def value(self, value: float):
        if value > self.__end:
            value = self.__end
        elif value < self.__start:
            value = self.__start
        self.__value = value
        self.__percent = (self.__value - self.__start) / (self.__end - self.__start)

class Scale(ProgressBar, Clickable):
    def __init__(self, master, command=None, state="normal",
                 highlight_color=(0, 0, 255), hover_sound=None, on_click_sound=None, **kwargs):
        ProgressBar.__init__(self, **kwargs)
        Clickable.__init__(self, master, command, state=state, highlight_color=highlight_color, hover_sound=hover_sound, on_click_sound=on_click_sound)
        master.bind_joystick_axis(0, "AXIS_LEFT_X", self.axis_event)
        master.bind_key(pygame.K_KP_MINUS, self.key_event, hold=True)
        master.bind_key(pygame.K_KP_PLUS, self.key_event, hold=True)

    def draw(self, surface: pygame.Surface) -> None:
        self.call_update()
        ProgressBar.draw(self, surface)

    def mouse_move_event(self, mouse_pos) -> None:
        if self.active:
            self.percent = (mouse_pos[0] - self.x) / self.width

    def axis_event(self, value) -> None:
        if self.has_focus() and self.active:
            self.percent += (0.01 * value)

    def key_event(self, key_value: int, key_state: bool) -> None:
        if self.has_focus():
            offset = 0
            if key_value == pygame.K_KP_MINUS:
                offset = -1
            elif key_value == pygame.K_KP_PLUS:
                offset = 1
            self.percent += offset * key_state * 0.005

    def on_click_down(self, event: Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_move_event(event.pos)

    def on_mouse_motion(self, mouse_pos: Tuple[int, int]) -> None:
        self.mouse_move_event(mouse_pos)

    def call_update(self):
        if hasattr(self, "command") and self.command is not None:
            self.command.__call__()

class CheckBox(RectangleShape, Clickable):
    def __init__(self, master, width: int, height: int, color: tuple, value=False, on_value=True, off_value=False,
                 outline=2, image: Optional[Image] = None, command: Optional[Callable[..., Any]] = None,
                 highlight_color=(0, 0, 255), state="normal", hover_sound=None, on_click_sound=None, **kwargs):
        RectangleShape.__init__(self, width, height, color, outline=outline, **kwargs)
        Clickable.__init__(self, master, self.change_value, state, highlight_color=highlight_color, hover_sound=hover_sound, on_click_sound=on_click_sound)
        self.__on_changed_value = command
        self.active_img = image
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
        if self.__on_changed_value is not None:
            self.__on_changed_value(self.__value)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_shown():
            RectangleShape.draw(self, surface)
            if self.value == self.__on_value:
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
    def change_value(self):
        self.value = not self.value