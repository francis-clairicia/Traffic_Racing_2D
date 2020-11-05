# -*- coding: Utf-8 -*

import pygame
from my_pygame import Window, Clickable, Button, ImageButton, Image, Text, ProgressBar, RectangleShape, ButtonListHorizontal, DrawableList
from my_pygame import GRAY, GRAY_LIGHT, YELLOW, GREEN, GREEN_LIGHT, GREEN_DARK, TRANSPARENT
from my_pygame import change_brightness
from constants import RESOURCES, CAR_INFOS, ENVIRONMENT
from save import SAVE
from .gameplay import Gameplay, format_number

class CarViewer(Clickable, Image):
    def __init__(self, master, car_id: int, **kwargs):
        self.__height = 150
        Image.__init__(self, RESOURCES.IMG["garage_cars"][car_id], height=self.__height)
        Clickable.__init__(self, master, **kwargs, highlight_thickness=0)

        self.__id = car_id
        self.__all_max_speed = list()
        self.__all_acceleration = list()
        self.__all_maniablities = list()
        self.__all_braking = list()
        for infos in CAR_INFOS.values():
            self.__all_max_speed.append(infos["max_speed"])
            self.__all_acceleration.append(infos["acceleration"])
            self.__all_maniablities.append(infos["maniability"])
            self.__all_braking.append(infos["braking"])

        self.take_focus(True)
        self.disable_key_joy()
        self.disable_mouse()
        self.master.bind_event(pygame.KEYDOWN, self.on_click_down)
        self.master.bind_event(pygame.KEYUP, self.on_click_up)
        self.master.bind_event(pygame.JOYHATMOTION, self.on_click_down)
        self.master.bind_event(pygame.JOYHATMOTION, self.on_click_up)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value: int):
        self.__id = int(value)
        if self.__id < 1:
            self.__id = 1
        elif self.__id > len(self):
            self.__id = len(self)
        self.load(RESOURCES.IMG["garage_cars"][self.__id], height=self.__height)

    @property
    def max_speed(self) -> int:
        return max(self.__all_max_speed) * 1.10

    @property
    def min_acceleration(self) -> int:
        return min(self.__all_acceleration) * 0.90

    @property
    def max_maniability(self) -> int:
        return max(self.__all_maniablities) * 1.30

    @property
    def min_braking(self) -> int:
        return min(self.__all_braking) * 0.80

    def __getitem__(self, key: str):
        return CAR_INFOS[self.id][key]

    def __len__(self):
        return len(CAR_INFOS)

    def on_focus_set(self):
        self.master.left_arrow.focus = True
        self.master.right_arrow.focus = True

    def on_focus_leave(self):
        self.master.left_arrow.focus = False
        self.master.right_arrow.focus = False

    def on_click_down(self, event: pygame.event.Event):
        if not self.has_focus():
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.master.left_arrow.is_shown():
                self.master.left_arrow.active = True
            elif event.key == pygame.K_RIGHT and self.master.right_arrow.is_shown():
                self.master.right_arrow.active = True
        elif event.type == pygame.JOYHATMOTION:
            if event.value[0] == -1 and self.master.left_arrow.is_shown():
                self.master.left_arrow.active = True
            elif event.value[0] == 1 and self.master.right_arrow.is_shown():
                self.master.right_arrow.active = True

    def on_click_up(self, event: pygame.event.Event):
        if not self.has_focus():
            return
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and self.master.left_arrow.is_shown():
                self.master.left_arrow.active = False
                self.play_on_click_sound()
                self.decrease_id()
            elif event.key == pygame.K_RIGHT and self.master.right_arrow.is_shown():
                self.master.right_arrow.active = False
                self.play_on_click_sound()
                self.increase_id()
        elif event.type == pygame.JOYHATMOTION:
            if self.master.left_arrow.active and event.value[0] == 0 and self.master.left_arrow.is_shown():
                self.master.left_arrow.active = False
                self.play_on_click_sound()
                self.decrease_id()
            elif self.master.right_arrow.active and event.value[0] == 0 and self.master.right_arrow.is_shown():
                self.master.right_arrow.active = False
                self.play_on_click_sound()
                self.increase_id()

    def increase_id(self):
        self.id += 1

    def decrease_id(self):
        self.id -= 1

class ConfirmPayement(Window):
    def __init__(self, master):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.bg = RectangleShape(*self.size, (0, 0, 0, 170))
        self.frame = RectangleShape(0.50 * self.width, 0.50 * self.height, GREEN, outline=3)
        self.text = Text("Are you sure you want\nto buy this car ?", (RESOURCES.FONT["algerian"], 60), justify=Text.T_CENTER)
        self.button_yes = Button(
            self, "Yes", self.text.font,
            bg=GREEN, hover_bg=GREEN_LIGHT, active_bg=GREEN_DARK,
            hover_sound=RESOURCES.SFX["select"], on_click_sound=RESOURCES.SFX["validate"],
            highlight_color=YELLOW, callback=self.buy
        )
        self.button_red_cross = ImageButton(
            self, img=RESOURCES.IMG["red_cross"],
            active_img=RESOURCES.IMG["red_cross_hover"],
            hover_sound=RESOURCES.SFX["select"], on_click_sound=RESOURCES.SFX["back"],
            callback=self.stop, highlight_color=YELLOW
        )
        self.buyed = False
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop(sound=RESOURCES.SFX["back"]))
        self.bind_joystick(0, "B", lambda event: self.stop(sound=RESOURCES.SFX["back"]))

    def place_objects(self):
        self.text.center = self.frame.center = self.center
        self.button_red_cross.move(left=self.frame.left + 5, top=self.frame.top + 5)
        self.button_yes.move(bottom=self.frame.bottom - 10, centerx=self.frame.centerx)

    def set_grid(self):
        self.button_red_cross.set_obj_on_side(on_bottom=self.button_yes)
        self.button_yes.set_obj_on_side(on_top=self.button_red_cross)

    def buy(self):
        self.buyed = True
        self.stop()

class EnvironmentChooser(Window):
    def __init__(self, master):
        Window.__init__(self, bg_color=master.bg_color, bg_music=master.bg_music)
        params_for_button = {
            "highlight_color": YELLOW,
            "hover_sound": RESOURCES.SFX["select"],
            "on_click_sound": RESOURCES.SFX["back"]
        }
        self.master = master
        self.button_back = ImageButton(self, img=RESOURCES.IMG["blue_arrow"], **params_for_button, callback=self.stop)

        self.objects.add(master.text_highscore, master.text_money)

        self.text_title = Text("ENVIRONMENT", (RESOURCES.FONT["algerian"], 90), GREEN_DARK, shadow=True, shadow_x=2, shadow_y=2)
        self.environment = ButtonListHorizontal(offset=15)
        self.texts = DrawableList()
        for name, color in ENVIRONMENT.items():
            b = Button(
                self, img=Image(RESOURCES.IMG[name], max_width=180, max_height=180), compound="center",
                outline=3, callback=lambda env=name: self.play(env), bg=color,
                hover_bg=change_brightness(color, 20), active_bg=change_brightness(color, -20),
                hover_sound=RESOURCES.SFX["select"], on_click_sound=RESOURCES.SFX["validate"], highlight_color=YELLOW
            )
            b.set_size(200)
            self.texts.add(Text(name.upper(), (RESOURCES.FONT["algerian"], 50), GREEN_DARK, shadow=True, shadow_x=2, shadow_y=2))
            self.environment.add(b)

        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop(sound=RESOURCES.SFX["back"]))
        self.bind_joystick(0, "B", lambda event: self.stop(sound=RESOURCES.SFX["back"]))

    def place_objects(self):
        self.button_back.topleft = (5, 5)
        self.environment.move(center=self.center)
        self.text_title.move(centerx=self.environment.centerx, bottom=self.environment.top - 10)
        for text, button in zip(self.texts, self.environment):
            text.move(top=button.bottom + 5, centerx=button.centerx)

    def set_grid(self):
        self.environment.set_obj_on_side(on_left=self.button_back, on_top=self.button_back)
        self.button_back.set_obj_on_side(on_bottom=self.environment[0], on_right=self.environment[0])
        self.environment[0].focus_set()

    def play(self, env: str):
        gameplay = Gameplay(self.master.car_viewer.id, env)
        gameplay.mainloop()
        if not gameplay.go_to_garage:
            self.master.stop()
        else:
            self.master.car_viewer.focus_set()
        self.stop()

class Garage(Window):

    def __init__(self):
        Window.__init__(self, bg_color=GRAY, bg_music=RESOURCES.MUSIC["garage"])
        params_for_all_buttons = {
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "highlight_color": YELLOW,
            "hover_sound": RESOURCES.SFX["select"],
        }
        params_for_button_except_back = {
            "on_click_sound": RESOURCES.SFX["validate"],
            "disabled_sound": RESOURCES.SFX["block"],
            "disabled_bg": GRAY_LIGHT,
        }
        params_for_button_except_back.update(params_for_all_buttons)
        params_for_car_viewer = {k: params_for_button_except_back[k] for k in ["hover_sound", "on_click_sound"]}
        self.button_back = ImageButton(self, RESOURCES.IMG["blue_arrow"], **params_for_all_buttons, on_click_sound=RESOURCES.SFX["back"], callback=self.stop)
        self.car_viewer = CarViewer(self, SAVE["car"], **params_for_car_viewer)

        size_progress_bar = (300, 30)
        self.speed_bar = ProgressBar(*size_progress_bar, TRANSPARENT, GREEN)
        self.maniability_bar = ProgressBar(*size_progress_bar, TRANSPARENT, GREEN)
        self.braking_bar = ProgressBar(*size_progress_bar, TRANSPARENT, GREEN)

        self.left_arrow = ImageButton(
            self, img=RESOURCES.IMG["left_arrow"], active_img=RESOURCES.IMG["left_arrow_hover"],
            **params_for_button_except_back, callback=self.car_viewer.decrease_id
        )
        self.right_arrow = ImageButton(
            self, img=RESOURCES.IMG["right_arrow"], active_img=RESOURCES.IMG["right_arrow_hover"],
            **params_for_button_except_back, callback=self.car_viewer.increase_id
        )
        for arrow in [self.left_arrow, self.right_arrow]:
            arrow.take_focus(False)
        self.button_price = Button(
            self, font=(RESOURCES.FONT["algerian"], 40), img=Image(RESOURCES.IMG["piece"], size=40), compound="right",
            callback=self.buy_car, **params_for_button_except_back
        )
        self.button_play = Button(
            self, "Play", font=(RESOURCES.FONT["algerian"], 70), callback=self.play,
            **params_for_button_except_back
        )
        self.text_money = Text(format_number(SAVE["money"]), (RESOURCES.FONT["algerian"], 50), YELLOW, img=Image(RESOURCES.IMG["piece"], height=40), compound="right")
        self.text_highscore = Text("Highscore: {}".format(SAVE["highscore"]), (RESOURCES.FONT["algerian"], 50), YELLOW)
        self.padlock = Image(RESOURCES.IMG["padlock"])
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop(sound=RESOURCES.SFX["back"]))
        self.bind_joystick(0, "B", lambda event: self.stop(sound=RESOURCES.SFX["back"]))

    def update(self):
        self.left_arrow.set_visibility(self.car_viewer.id > 1)
        self.right_arrow.set_visibility(self.car_viewer.id < len(self.car_viewer))
        if not SAVE["owned_cars"][self.car_viewer.id]:
            self.padlock.show()
            price = self.car_viewer["price"]
            if isinstance(price, int):
                self.button_price.show()
                self.button_price.text = format_number(price)
                self.button_price.state = Button.NORMAL if SAVE["money"] >= price else Button.DISABLED
            else:
                self.button_price.hide()
            self.button_play.state = Button.DISABLED
        else:
            self.padlock.hide()
            self.button_price.hide()
            self.button_play.state = Button.NORMAL
            SAVE["car"] = self.car_viewer.id
        max_s = self.car_viewer.max_speed
        min_a = self.car_viewer.min_acceleration
        max_m = self.car_viewer.max_maniability
        min_b = self.car_viewer.min_braking
        s = self.car_viewer["max_speed"]
        a = self.car_viewer["acceleration"]
        m = self.car_viewer["maniability"]
        b = self.car_viewer["braking"]
        self.speed_bar.percent = (s + min_a)/(max_s + a)
        self.maniability_bar.percent = m / max_m
        self.braking_bar.percent = min_b / b

    def place_objects(self):
        self.button_back.topleft = (5, 5)
        self.car_viewer.move(center=self.center)
        self.padlock.center = self.car_viewer.center

        self.braking_bar.move(bottom=self.car_viewer.top - 40, centerx=self.car_viewer.centerx + 100)
        self.maniability_bar.move(bottom=self.braking_bar.top - 10, centerx=self.car_viewer.centerx + 100)
        self.speed_bar.move(bottom=self.maniability_bar.top - 10, centerx=self.car_viewer.centerx + 100)

        self.speed_bar.show_label("Speed/Acc.", ProgressBar.S_LEFT, font=(RESOURCES.FONT["algerian"], 40))
        self.maniability_bar.show_label("Maniability", ProgressBar.S_LEFT, font=(RESOURCES.FONT["algerian"], 40))
        self.braking_bar.show_label("Braking", ProgressBar.S_LEFT, font=(RESOURCES.FONT["algerian"], 40))

        self.left_arrow.move(left=self.left + 50, centery=self.centery)
        self.right_arrow.move(right=self.right - 50, centery=self.centery)
        self.button_price.move(centerx=self.centerx, top=self.car_viewer.bottom + 25)
        self.button_play.move(bottom=self.bottom - 50, right=self.right - 10)

        self.text_money.move(top=5, right=self.right - 10)
        self.text_highscore.move(bottom=self.bottom - 50, left=5)

    def set_grid(self):
        self.button_back.set_obj_on_side(on_bottom=self.car_viewer)
        self.car_viewer.set_obj_on_side(on_top=self.button_back, on_bottom=self.button_price)
        self.button_price.set_obj_on_side(on_top=self.car_viewer, on_bottom=self.button_play)
        self.button_play.set_obj_on_side(on_top=self.button_price)

    def buy_car(self):
        confirm_window = ConfirmPayement(self)
        confirm_window.mainloop()
        if confirm_window.buyed:
            SAVE["money"] -= self.car_viewer["price"]
            SAVE["owned_cars"][self.car_viewer.id] = True
            self.text_money.message = format_number(SAVE["money"])
            if Clickable.MODE != Clickable.MODE_MOUSE:
                self.car_viewer.focus_set()

    def play(self):
        environment_chooser = EnvironmentChooser(self)
        environment_chooser.mainloop()
        self.text_money.message = format_number(SAVE["money"])
        self.text_highscore.message = "Highscore: {}".format(SAVE["highscore"])