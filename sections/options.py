# -*- coding: Utf-8 -*

import pygame
from my_pygame import Window, RectangleShape, Text, Button, ImageButton, Image, CheckBox, Scale
from my_pygame import GREEN, GREEN_DARK, TRANSPARENT, YELLOW, RED, RED_DARK, RED_LIGHT, WHITE, BLACK, GRAY_DARK, GRAY
from my_pygame.gamepad_viewer import GamepadViewer
from constants import RESOURCES
from save import SAVE

class AssignmentPrompt(Window):
    def __init__(self, master: Window, action: str):
        Window.__init__(self, master=master, bg_music=master.bg_music)

        self.action = action

        self.bg = RectangleShape(self.width, self.height, (0, 0, 0, 170))
        self.frame = RectangleShape(0.4 * self.width, 0.4 * self.height, BLACK, outline=3, outline_color=WHITE)
        self.escape = Text("Echap (clavier) ou bouton START (manette): Annuler", font=("calibri", 30), color=WHITE)
        self.instruction = Text("Appuyez sur une touche", font=("calibri", 50), color=WHITE)

        for event in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYHATMOTION):
            self.bind_event(event, self.choose)
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop(sound=RESOURCES.SFX["back"]))
        self.bind_joystick(0, "START", lambda event: self.stop(sound=RESOURCES.SFX["back"]))

    def place_objects(self):
        self.instruction.center = self.frame.center = self.center
        self.escape.move(left=self.frame.left + 5, top=self.frame.top + 5)

    def choose(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE and event.key in self.keyboard:
            SAVE["controls"][self.action]["key"] = self.keyboard[event.key]
            self.stop(sound=RESOURCES.SFX["validate"])
        elif event.type == pygame.JOYBUTTONDOWN and event.instance_id == self.joystick[0].id:
            button = self.joystick[0].search_key("button", event.button)
            if button != "START":
                SAVE["controls"][self.action]["joy"] = button
                self.stop(sound=RESOURCES.SFX["validate"])
        elif event.type == pygame.JOYAXISMOTION and event.instance_id == self.joystick[0].id and abs(event.value) >= 0.9:
            SAVE["controls"][self.action]["joy"] = self.joystick[0].search_key("axis", event.axis, axis=-1 if event.value < 0 else 1)
            self.stop(sound=RESOURCES.SFX["validate"])
        elif event.type == pygame.JOYHATMOTION and event.instance_id == self.joystick[0].id and (event.value != (0, 0)):
            SAVE["controls"][self.action]["joy"] = self.joystick[0].search_key("hat", event.hat, hat_value=event.value)
            self.stop(sound=RESOURCES.SFX["validate"])

class Options(Window):
    def __init__(self, master: Window):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.frame = RectangleShape(0.60 * self.width, 0.60 * self.height, GREEN, outline=3)
        self.title = Text("Options", font=(RESOURCES.FONT["algerian"], 70))
        self.text_gp_viewer = Text("F12: Gamepad viewer", (RESOURCES.FONT["algerian"], 20))

        self.options_font = (RESOURCES.FONT["algerian"], 40)
        self.case_font = (RESOURCES.FONT["algerian"], 30)
        self.control_font = ("calibri", 20)
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
            "hover_sound": RESOURCES.SFX["select"],
            "disabled_sound": RESOURCES.SFX["block"]
        }
        params_for_option_buttons = {
            "on_click_sound": RESOURCES.SFX["validate"]
        }
        params_for_buttons = {
            "bg": GRAY_DARK,
            "fg": WHITE,
            "hover_bg": GRAY,
            "active_bg": BLACK
        }
        params_for_reset_button = {
            "bg": RED,
            "fg": WHITE,
            "hover_bg": RED_LIGHT,
            "active_bg": RED_DARK,
        }

        self.button_back = ImageButton(
            self, img=RESOURCES.IMG["blue_arrow"],
            on_click_sound=RESOURCES.SFX["back"], callback=self.stop,
            **params_for_all_buttons
        )
        self.button_change_page = Button(
            self, ">>", font=self.case_font, callback=self.change_page,
            **params_for_all_buttons, **params_for_option_buttons, **params_for_buttons
        )
        self.nb_pages = 2
        self.page = 1

        ## PAGE 1 ##
        valid_img = Image(RESOURCES.IMG["green_valid"])
        self.text_music = Text("Music:", self.options_font)
        self.cb_music = CheckBox(
            self, 30, 30, TRANSPARENT, image=valid_img,
            value=self.get_music_state(), callback=self.set_music_state,
            **params_for_all_buttons, **params_for_option_buttons
        )
        self.scale_music = Scale(
            self, **params_for_all_scales, **params_for_all_buttons,
            height=self.cb_music.height, default=Window.music_volume() * 100,
            callback=lambda self=self: self.set_music_volume(self.scale_music.percent)
        )
        self.text_sound = Text("SFX:", self.options_font)
        self.cb_sound = CheckBox(
            self, 30, 30, TRANSPARENT, image=valid_img,
            value=self.get_sound_state(), callback=self.set_sound_state,
            **params_for_all_buttons, **params_for_option_buttons
        )
        self.scale_sound = Scale(
            self, **params_for_all_scales, **params_for_all_buttons,
            height=self.cb_sound.height, default=Window.sound_volume() * 100,
            callback=lambda self=self: self.set_sound_volume(self.scale_sound.percent)
        )
        self.text_fps = Text("FPS:", self.options_font)
        self.cb_show_fps = CheckBox(
            self, 30, 30, TRANSPARENT, image=valid_img,
            value=Window.fps_is_shown(), callback=self.show_fps,
            **params_for_all_buttons, **params_for_option_buttons
        )
        self.button_reset = Button(
            self, "Reset Save", font=(RESOURCES.FONT["algerian"], 30), callback=SAVE.reset, state=Button.DISABLED,
            **params_for_all_buttons, **params_for_option_buttons, **params_for_reset_button
        )
        ## PAGE 2 ##
        self.text_acceleration = Text("Accélérer:", self.options_font)
        self.button_auto_acceleration = Button(
            self, font=self.case_font, callback=lambda: SAVE.update(auto_acceleration=not SAVE["auto_acceleration"]),
            **params_for_all_buttons, **params_for_option_buttons, **params_for_buttons
        )
        self.button_acceleration = Button(
            self, font=self.control_font, callback=lambda: self.choose_key("speed_up"),
            **params_for_all_buttons, **params_for_option_buttons, **params_for_buttons
        )
        self.text_brake = Text("Freiner:", self.options_font)
        self.button_brake = Button(
            self, font=self.control_font, callback=lambda: self.choose_key("brake"),
            **params_for_all_buttons, **params_for_option_buttons, **params_for_buttons
        )
        self.text_move_up = Text("Aller en haut:", self.options_font)
        self.button_move_up = Button(
            self, font=self.control_font, callback=lambda: self.choose_key("up"),
            **params_for_all_buttons, **params_for_option_buttons, **params_for_buttons
        )
        self.text_move_down = Text("Aller en bas:", self.options_font)
        self.button_move_down = Button(
            self, font=self.control_font, callback=lambda: self.choose_key("down"),
            **params_for_all_buttons, **params_for_option_buttons, **params_for_buttons
        )

        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop(sound=RESOURCES.SFX["back"]))
        self.bind_joystick(0, "B", lambda event: self.stop(sound=RESOURCES.SFX["back"]))
        self.bind_key(pygame.K_F12, lambda event: self.open_joystick_viewer())

    def on_quit(self):
        SAVE.dump()

    def change_page(self):
        self.page = (self.page % self.nb_pages) + 1

    def update(self):
        self.hide_all(without=[self.frame, self.title, self.text_gp_viewer, self.button_back, self.button_change_page])
        if self.page == 1:
            self.text_music.show()
            self.text_sound.show()
            for checkbox, scale in [(self.cb_music, self.scale_music), (self.cb_sound, self.scale_sound)]:
                checkbox.show()
                if checkbox.value is True:
                    scale.show()
                    checkbox.set_obj_on_side(on_right=scale)
                else:
                    checkbox.set_obj_on_side(on_right=self.button_change_page)
            self.text_fps.show()
            self.cb_show_fps.show()
            self.button_reset.show()
            self.button_back.set_obj_on_side(on_bottom=self.cb_music, on_right=self.cb_music)
            self.button_change_page.set_obj_on_side(on_top=self.cb_show_fps, on_left=self.button_reset)
        elif self.page == 2:
            self.text_acceleration.show()
            self.button_auto_acceleration.set_text("Automatique" if SAVE["auto_acceleration"] else "Manuel")
            self.button_auto_acceleration.show()
            control_text_format = "Key: {key}\nJoystick: {joy}"
            if not SAVE["auto_acceleration"]:
                self.button_acceleration.set_text(control_text_format.format(**SAVE["controls"]["speed_up"]))
                self.button_acceleration.move(left=self.button_auto_acceleration.right + 10, centery=self.button_auto_acceleration.centery)
                self.button_acceleration.show()
                self.button_auto_acceleration.set_obj_on_side(on_right=self.button_acceleration)
            else:
                self.button_auto_acceleration.set_obj_on_side(on_right=self.button_back)
            fields = [
                (self.text_brake, self.button_brake, "brake"),
                (self.text_move_up, self.button_move_up, "up"),
                (self.text_move_down, self.button_move_down, "down"),
            ]
            for text, button, action in fields:
                text.show()
                button.set_text(control_text_format.format(**SAVE["controls"][action]))
                button.show()
            self.button_back.set_obj_on_side(on_bottom=self.button_auto_acceleration, on_right=self.button_auto_acceleration)
            self.button_change_page.set_obj_on_side(on_top=self.button_move_down, on_left=self.button_move_down)

    def place_objects(self):
        self.frame.move(center=self.center)
        self.title.move(top=self.frame.top + 10, centerx=self.frame.centerx)
        self.text_gp_viewer.move(top=self.frame.top + 5, right=self.frame.right - 5)
        self.button_back.move(top=self.frame.top + 5, left=self.frame.left + 5)
        self.button_change_page.move(bottom=self.frame.bottom - 5, right=self.frame.right - 5)
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
        ## PAGE 2 ##
        self.text_acceleration.move(left=self.frame.left + 10, top=self.title.bottom + 50)
        self.button_auto_acceleration.move(left=self.text_acceleration.right + 10, centery=self.text_acceleration.centery)
        self.text_brake.move(left=self.text_acceleration.left, top=self.text_acceleration.bottom + 50)
        self.button_brake.move(left=self.text_brake.right + 10, centery=self.text_brake.centery)
        self.text_move_up.move(left=self.text_acceleration.left, top=self.text_brake.bottom + 50)
        self.button_move_up.move(left=self.text_move_up.right + 10, centery=self.text_move_up.centery)
        self.text_move_down.move(left=self.text_acceleration.left, top=self.text_move_up.bottom + 50)
        self.button_move_down.move(left=self.text_move_down.right + 10, centery=self.text_move_down.centery)

    def set_grid(self):
        ## PAGE 1 ##
        self.cb_music.set_obj_on_side(on_top=self.button_back, on_left=self.button_back, on_bottom=self.cb_sound)
        self.scale_music.set_obj_on_side(on_top=self.button_back, on_left=self.cb_music, on_bottom=self.scale_sound, on_right=self.button_change_page)
        self.cb_sound.set_obj_on_side(on_top=self.cb_music, on_left=self.button_back, on_bottom=self.cb_show_fps)
        self.scale_sound.set_obj_on_side(on_top=self.scale_music, on_left=self.cb_sound, on_bottom=self.cb_show_fps, on_right=self.button_change_page)
        self.cb_show_fps.set_obj_on_side(on_left=self.button_back, on_top=self.cb_sound, on_bottom=self.button_reset, on_right=self.button_change_page)
        self.button_reset.set_obj_on_side(on_left=self.button_back, on_top=self.cb_show_fps, on_right=self.button_change_page)
        ## PAGE 2 ##
        self.button_auto_acceleration.set_obj_on_side(on_top=self.button_back, on_left=self.button_back, on_bottom=self.button_brake)
        self.button_acceleration.set_obj_on_side(on_top=self.button_back, on_left=self.button_auto_acceleration, on_bottom=self.button_brake, on_right=self.button_change_page)
        self.button_brake.set_obj_on_side(on_top=self.button_auto_acceleration, on_left=self.button_back, on_bottom=self.button_move_up, on_right=self.button_change_page)
        self.button_move_up.set_obj_on_side(on_top=self.button_brake, on_left=self.button_back, on_bottom=self.button_move_down, on_right=self.button_change_page)
        self.button_move_down.set_obj_on_side(on_top=self.button_move_up, on_left=self.button_back, on_bottom=self.button_change_page, on_right=self.button_change_page)

    def choose_key(self, action: str):
        AssignmentPrompt(self, action).mainloop()

    def open_joystick_viewer(self):
        GamepadViewer(self).mainloop()