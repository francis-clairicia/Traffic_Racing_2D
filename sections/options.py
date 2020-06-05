# -*- coding: Utf-8 -*

import pygame
from my_pygame import Window, RectangleShape, Text, ImageButton, Image, CheckBox, Scale
from my_pygame import GREEN, GREEN_DARK, TRANSPARENT, YELLOW, BLACK
from constants import FONT, AUDIO, IMG

class Options(Window):
    def __init__(self, master: Window):
        Window.__init__(self, master=master, bg_color=None)
        self.bind_joystick_button(0, "B", lambda event: self.stop())
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())
        self.frame = RectangleShape(0.40 * self.width, 0.40 * self.height, GREEN, outline=3)
        self.title = Text("Options", font=(FONT["algerian"], 70), color=BLACK)

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

        self.button_back = ImageButton(self, Image(IMG["blue_arrow"]), **params_for_all_buttons, command=self.stop)
        self.page = 1

        ## PAGE 1 ##
        self.text_music = Text("Music:", self.options_font, BLACK)
        self.cb_music = CheckBox(
            self, 30, 30, TRANSPARENT, image=Image(IMG["green_valid"]),
            state=self.get_music_state(), command=self.set_music_state,
            **params_for_all_buttons, **params_for_option_buttons)
        self.scale_music = Scale(
            self, **params_for_all_scales, **params_for_all_buttons,
            height=self.cb_music.height, default=Window.music_volume() * 100,
            command=lambda self=self: self.set_music_volume(self.scale_music.percent)
        )
        self.text_sound = Text("SFX:", self.options_font, BLACK)
        self.cb_sound = CheckBox(
            self, 30, 30, TRANSPARENT, image=Image(IMG["green_valid"]),
            state=self.get_sound_state(), command=self.set_sound_state,
            **params_for_all_buttons, **params_for_option_buttons)
        self.scale_sound = Scale(
            self, **params_for_all_scales, **params_for_all_buttons,
            height=self.cb_sound.height, default=Window.sound_volume() * 100,
            command=lambda self=self: self.set_sound_volume(self.scale_sound.percent)
        )

    def on_quit(self):
        self.play_sound(AUDIO["back"])

    def update(self):
        self.hide_all(without=[self.frame, self.title, self.button_back])
        if self.page == 1:
            self.text_music.show()
            self.text_sound.show()
            for checkbox, scale in [(self.cb_music, self.scale_music), (self.cb_sound, self.scale_sound)]:
                checkbox.show()
                if checkbox.state is True:
                    scale.show()
                    checkbox.set_obj_on_side(on_right=scale)
                else:
                    checkbox.remove_obj_on_side("on_right")

    def place_objects(self):
        self.frame.move(center=self.center)
        self.title.move(top=self.frame.top + 10, centerx=self.frame.centerx)
        self.button_back.move(top=self.frame.top + 5, left=self.frame.left + 5)
        ## PAGE 1 ##
        self.text_music.move(left=self.frame.left + 10, top=self.title.bottom + 10)
        self.text_sound.move(right=self.text_music.right, top=self.text_music.bottom + 5)
        self.cb_music.move(left=self.text_music.right + 10, centery=self.text_music.centery)
        self.cb_sound.move(left=self.text_music.right + 10, centery=self.text_sound.centery)
        self.scale_music.move(left=self.cb_music.right + 50, centery=self.cb_music.centery)
        self.scale_music.show_value(self.case_font, BLACK, Scale.S_RIGHT)
        self.scale_sound.move(left=self.cb_sound.right + 50, centery=self.cb_sound.centery)
        self.scale_sound.show_value(self.case_font, BLACK, Scale.S_RIGHT)

    def set_grid(self):
        self.button_back.set_obj_on_side(on_bottom=self.cb_music, on_right=self.cb_music)
        self.cb_music.set_obj_on_side(on_top=self.button_back, on_left=self.button_back, on_bottom=self.cb_sound)
        self.scale_music.set_obj_on_side(on_top=self.button_back, on_left=self.cb_music, on_bottom=self.scale_sound)
        self.cb_sound.set_obj_on_side(on_top=self.cb_music, on_left=self.button_back)
        self.scale_sound.set_obj_on_side(on_top=self.scale_music, on_left=self.cb_sound)