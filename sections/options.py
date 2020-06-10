# -*- coding: Utf-8 -*

import pygame
from my_pygame import Window, RectangleShape, Text, Button, ImageButton, Image, CheckBox, Scale
from my_pygame import GREEN, GREEN_DARK, TRANSPARENT, YELLOW, RED, RED_DARK, RED_LIGHT, WHITE
from constants import FONT, AUDIO, IMG
from save import SAVE

class Options(Window):
    def __init__(self, master: Window):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.frame = RectangleShape(0.60 * self.width, 0.60 * self.height, GREEN, outline=3)
        self.title = Text("Options", font=(FONT["algerian"], 70))

        self.options_font = (FONT["algerian"], 40)
        self.case_font = (FONT["algerian"], 30)
        params_for_all_scales = {
            "width": 0.45 * self.frame.w,
            "color": TRANSPARENT,
            "scale_color": GREEN_DARK,
            "from_": 0,
            "to": 100,
            "outline": 3,
        }
        params_for_all_buttons = {
            "highlight_color": YELLOW,
            "hover_sound": AUDIO["select"],
        }
        params_for_option_buttons = {
            "on_click_sound": AUDIO["validate"]
        }
        params_for_reset_button = {
            "bg": RED,
            "fg": WHITE,
            "hover_bg": RED_LIGHT,
            "active_bg": RED_DARK,
        }

        self.button_back = ImageButton(self, Image(IMG["blue_arrow"]), on_click_sound=AUDIO["back"], **params_for_all_buttons, command=self.stop)
        self.page = 1

        ## PAGE 1 ##
        valid_img = Image(IMG["green_valid"])
        self.text_music = Text("Music:", self.options_font)
        self.cb_music = CheckBox(
            self, 30, 30, TRANSPARENT, image=valid_img,
            value=self.get_music_state(), command=self.set_music_state,
            **params_for_all_buttons, **params_for_option_buttons
        )
        self.scale_music = Scale(
            self, **params_for_all_scales, **params_for_all_buttons,
            height=self.cb_music.height, default=Window.music_volume() * 100,
            command=lambda self=self: self.set_music_volume(self.scale_music.percent)
        )
        self.text_sound = Text("SFX:", self.options_font)
        self.cb_sound = CheckBox(
            self, 30, 30, TRANSPARENT, image=valid_img,
            value=self.get_sound_state(), command=self.set_sound_state,
            **params_for_all_buttons, **params_for_option_buttons
        )
        self.scale_sound = Scale(
            self, **params_for_all_scales, **params_for_all_buttons,
            height=self.cb_sound.height, default=Window.sound_volume() * 100,
            command=lambda self=self: self.set_sound_volume(self.scale_sound.percent)
        )
        self.text_fps = Text("FPS:", self.options_font)
        self.cb_show_fps = CheckBox(
            self, 30, 30, TRANSPARENT, image=valid_img,
            value=Window.fps_is_shown(), command=self.show_fps,
            **params_for_all_buttons, **params_for_option_buttons
        )
        self.button_reset = Button(
            self, "Reset Save", font=(FONT["algerian"], 30), command=SAVE.reset,
            **params_for_all_buttons, **params_for_option_buttons, **params_for_reset_button
        )

        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop(sound=self.button_back.on_click_sound))
        self.bind_joystick_button(0, "B", lambda event: self.stop(sound=self.button_back.on_click_sound))

    def update(self):
        self.hide_all(without=[self.frame, self.title, self.button_back])
        if self.page == 1:
            self.text_music.show()
            self.text_sound.show()
            for checkbox, scale in [(self.cb_music, self.scale_music), (self.cb_sound, self.scale_sound)]:
                checkbox.show()
                if checkbox.value is True:
                    scale.show()
                    checkbox.set_obj_on_side(on_right=scale)
                else:
                    checkbox.remove_obj_on_side("on_right")
            self.text_fps.show()
            self.cb_show_fps.show()
            self.button_reset.show()
        self.save_update()

    def save_update(self):
        SAVE["fps"] = self.cb_show_fps.value

    def place_objects(self):
        self.frame.move(center=self.center)
        self.title.move(top=self.frame.top + 10, centerx=self.frame.centerx)
        self.button_back.move(top=self.frame.top + 5, left=self.frame.left + 5)
        ## PAGE 1 ##
        self.text_music.move(left=self.frame.left + 10, top=self.title.bottom + 10)
        self.text_sound.move(right=self.text_music.right, top=self.text_music.bottom + 5)
        self.cb_music.move(left=self.text_music.right + 10, centery=self.text_music.centery)
        self.cb_sound.move(left=self.text_music.right + 10, centery=self.text_sound.centery)
        self.scale_music.move(centerx=self.frame.centerx, centery=self.cb_music.centery)
        self.scale_music.show_value(Scale.S_RIGHT, font=self.case_font)
        self.scale_sound.move(centerx=self.frame.centerx, centery=self.cb_sound.centery)
        self.scale_sound.show_value(Scale.S_RIGHT, font=self.case_font)
        self.text_fps.move(right=self.text_music.right, top=self.text_sound.bottom + 50)
        self.cb_show_fps.move(left=self.text_fps.right + 10, centery=self.text_fps.centery)
        self.button_reset.move(bottom=self.frame.bottom - 5, left=self.frame.left + 5)

    def set_grid(self):
        self.button_back.set_obj_on_side(on_bottom=self.cb_music, on_right=self.cb_music)
        self.cb_music.set_obj_on_side(on_top=self.button_back, on_left=self.button_back, on_bottom=self.cb_sound)
        self.scale_music.set_obj_on_side(on_top=self.button_back, on_left=self.cb_music, on_bottom=self.scale_sound)
        self.cb_sound.set_obj_on_side(on_top=self.cb_music, on_left=self.button_back, on_bottom=self.cb_show_fps)
        self.scale_sound.set_obj_on_side(on_top=self.scale_music, on_left=self.cb_sound, on_bottom=self.cb_show_fps)
        self.cb_show_fps.set_obj_on_side(on_left=self.button_back, on_top=self.cb_sound)