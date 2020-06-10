# -*- coding: Utf-8 -*

import random
from typing import Dict, Union
import pygame
from my_pygame import Window, RectangleShape, Text, Image, Button
from my_pygame import DrawableListHorizontal, DrawableListVertical
from my_pygame import ButtonListHorizontal, ButtonListVertical
from my_pygame import Sprite, CountDown, Clock
from my_pygame import GRAY, WHITE, BLACK, YELLOW, GREEN, GREEN_LIGHT, GREEN_DARK
from constants import IMG, AUDIO, FONT, CAR_INFOS
from save import SAVE
from .options import Options

def format_number(number: float) -> str:
    return f"{number:,}".replace(",", " ")

class Car(Sprite):
    def __init__(self, *img_list):
        Sprite.__init__(self, *img_list, height=55)
        self.speed = 30

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, value: float):
        value = float(value)

        min_value = 30
        max_value = 150
        ratio_min = 10
        ratio_max = 50
        ratio_coeff = (ratio_min - ratio_max) / (max_value - min_value)

        if value < 0:
            value = 0
        elif hasattr(self, "max_speed") and value > getattr(self, "max_speed"):
            value = getattr(self, "max_speed")
        self.__speed = value

        if self.__speed > 0:
            self.ratio = ratio_coeff * self.__speed + (ratio_max - ratio_coeff * min_value)
            if self.ratio < ratio_min:
                self.ratio = ratio_min
            elif self.ratio > ratio_max:
                self.ratio = ratio_max
            if not self.animated():
                self.start_animation(loop=True)
        else:
            self.stop_animation(reset=False)

class PlayerCar(Car):
    def __init__(self, car_id: int):
        Car.__init__(self, *IMG["gameplay_cars"][car_id])

        self.__speed_up = False
        self.__speed_up_offset = 0
        self.__braking = False
        self.__braking_offset = 0
        self.__move = False
        self.__move_offset = 0
        self.__speed_clock = Clock()
        self.__speed_time = 10 #ms
        self.__move_clock = Clock()
        self.__move_time = 10 #ms
        self.__crashed = False
        self.__speed_on_crash = 0

        infos = CAR_INFOS[car_id]
        self.max_speed = infos["max_speed"]
        self.acceleration = infos["acceleration"] * 1000
        self.maniability = infos["maniability"]
        self.braking = infos["braking"] * 1000

    def update(self, *args, **kwargs):
        if not self.__crashed and self.__speed_clock.elapsed_time(self.__speed_time):
            if self.__braking:
                self.speed -= (self.__speed_time * self.max_speed / self.braking) * self.__braking_offset
                if self.speed < 30:
                    self.speed = 30
            elif self.__speed_up:
                self.speed += (self.__speed_time * 100 / self.acceleration) * self.__speed_up_offset
            else:
                ratio = 5 # percent
                lost_speed = self.speed * ratio / 100
                self.speed -= self.__speed_time * lost_speed / 1000
                if self.speed < 30:
                    self.speed = 30
            self.__speed_up = False
            self.__braking = False
        if self.__move_clock.elapsed_time(self.__move_time):
            if not self.__crashed:
                if self.__move:
                    self.move_ip(0, (self.__move_time * self.maniability / 1000) * self.__move_offset)
                self.__move = False
            else:
                pixel_per_ms = args[0]
                x = (-self.__speed_on_crash) * pixel_per_ms
                self.move_ip(x, 0)

    def is_crashed(self):
        return self.__crashed

    def crash(self, car: Car):
        self.__speed_on_crash = self.speed
        self.speed = car.speed = 0
        self.__crashed = True

    def restart(self):
        self.__crashed = False
        self.__speed_on_crash = 0

    def speed_up(self, offset=1):
        if not self.__speed_up:
            self.__speed_up = True
            self.__speed_up_offset = offset

    def brake(self, offset=1):
        if not self.__braking:
            self.__braking = True
            self.__braking_offset = offset

    def moveUp(self, offset=1):
        if not self.__move:
            self.__move = True
            self.__move_offset = -offset

    def moveDown(self, offset=1):
        if not self.__move:
            self.__move = True
            self.__move_offset = offset

class TrafficCar(Car):
    def __init__(self, car_id: int, way: int):
        side = "opposé" if way in [0, 1] else "normal"
        Car.__init__(self, *IMG["traffic"][side][car_id])
        self.way = way
        self.side = 1 if side == "normal" else -1
        self.speed = (35, 40, 50, 60)[car_id - 1]

    def update(self, *args, **kwargs):
        player_car_speed, pixel_per_ms = args
        x = (self.speed * self.side - player_car_speed) * pixel_per_ms
        self.move_ip(x, 0)

class Info(Text):
    def __init__(self, title: str, *args, extension="", round_n=1, **kwargs):
        Text.__init__(self, str(), *args, **kwargs)
        self.__title = title
        self.__extension = extension
        self.__round_n = round_n
        self.value = 0

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("value must be an integer or a float")
        self.__value = value
        msg = self.__title + "\n" + str(round(value, self.__round_n) if self.__round_n > 0 else round(value))
        if len(self.__extension) > 0:
            msg += " " + self.__extension
        self.string = msg

class Pause(Window):
    def __init__(self, master):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())
        self.bind_joystick_button(0, "START", lambda event: self.stop())
        self.bind_joystick_button(0, "B", lambda event: self.stop())
        self.master = master
        self.bg = RectangleShape(*self.size, (0, 0, 0, 170))
        params_for_all_buttons = {
            "font": (FONT["algerian"], 100),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "hover_sound": AUDIO["select"],
            "on_click_sound": AUDIO["validate"],
            "outline": 3,
            "highlight_color": YELLOW
        }
        self.menu_buttons = ButtonListVertical(offset=30)
        self.menu_buttons.add_object(
            Button(self, "Return", **params_for_all_buttons, command=self.stop),
            Button(self, "Options", **params_for_all_buttons, command=self.show_options),
            Button(self, "Garage", **params_for_all_buttons, command=self.return_to_garage),
            Button(self, "Menu", **params_for_all_buttons, command=self.return_to_menu)
        )

    def place_objects(self):
        self.menu_buttons.center = self.center

    def show_options(self):
        self.hide_all(without=[self.bg])
        Options(self).mainloop()
        self.show_all()

    def return_to_garage(self):
        self.master.go_to_garage = True
        self.master.stop()
        self.stop()

    def return_to_menu(self):
        self.master.stop()
        self.stop()

class EndGame(Window):
    def __init__(self, master, score: int, distance: float, time_100: float, time_opposite: float):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.master = master
        self.bg = RectangleShape(*self.size, (0, 0, 0, 170))
        self.text_score = Text(f"Your score\n{score}", (FONT["algerian"], 120), YELLOW, justify="center")
        self.img_highscore = Image(IMG["new_high_score"], width=150)
        if score > SAVE["highscore"]:
            SAVE["highscore"] = score
        else:
            self.img_highscore.hide()

        MAX_MONEY = pow(10, 9) - 1
        money_distance = round(300.40 * distance)
        money_time_100 = round(12.5 * time_100)
        money_time_opposite = round(21.7 * time_opposite)
        money_gained = money_distance + money_time_100 + money_time_opposite
        total = SAVE["money"] + money_gained
        SAVE["money"] = MAX_MONEY if total > MAX_MONEY else total
        self.text_money = Text(format_number(SAVE["money"]), (FONT["algerian"], 50), YELLOW, img=Image(IMG["piece"], height=40), compound="right")

        font = ("calibri", 50)
        self.frame = RectangleShape(0.75 * self.width, 0.45 * self.height, BLACK, outline=1, outline_color=WHITE)
        self.text_distance = Text(f"Distance: {distance}", font, WHITE)
        self.img_green_arrow_distance = Image(IMG["green_arrow"], height=40)
        self.text_money_distance = Text(money_distance, font, WHITE, img=Image(IMG["piece"], height=40), compound="right")
        self.text_time_100 = Text(f"Time up to 100km: {time_100}", font, WHITE)
        self.img_green_arrow_time_100 = Image(IMG["green_arrow"], height=40)
        self.text_money_time_100 = Text(money_time_100, font, WHITE, img=Image(IMG["piece"], height=40), compound="right")
        self.text_time_opposite = Text(f"Time in opposite side: {time_opposite}", font, WHITE)
        self.img_green_arrow_time_opposite = Image(IMG["green_arrow"], height=40)
        self.text_money_time_opposite = Text(money_time_opposite, font, WHITE, img=Image(IMG["piece"], height=40), compound="right")
        self.total_money = DrawableListHorizontal(offset=10)
        self.total_money.add_object(
            Text("TOTAL: ", font, WHITE),
            Text(money_gained, font, WHITE, img=Image(IMG["piece"], height=40), compound="right")
        )

        params_for_all_buttons = {
            "font": (FONT["algerian"], 80),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "hover_sound": AUDIO["select"],
            "on_click_sound": AUDIO["validate"],
            "outline": 3,
            "highlight_color": YELLOW
        }
        self.menu_buttons = ButtonListHorizontal(offset=30)
        self.menu_buttons.add_object(
            Button(self, "Restart", **params_for_all_buttons, command=self.restart_game),
            Button(self, "Garage", **params_for_all_buttons, command=self.return_to_garage),
            Button(self, "Menu", **params_for_all_buttons, command=self.return_to_menu)
        )

    def place_objects(self):
        self.text_money.move(top=5, right=self.right - 10)

        self.text_score.move(centerx=self.centerx, centery=self.top + 0.25 * self.height)
        self.img_highscore.move(left=self.text_score.right, centery=self.text_score.centery)

        offset = self.frame.height / 6
        self.frame.move(centerx=self.centerx, top=0.75 * self.centery)
        self.text_distance.move(left=self.frame.left + 5, top=self.frame.top + 10)
        self.text_time_100.move(left=self.frame.left + 5, top=self.text_distance.bottom + offset)
        self.text_time_opposite.move(left=self.frame.left + 5, top=self.text_time_100.bottom + offset)
        self.img_green_arrow_distance.move(left=self.frame.centerx + 75, centery=self.text_distance.centery)
        self.img_green_arrow_time_100.move(left=self.frame.centerx + 75, centery=self.text_time_100.centery)
        self.img_green_arrow_time_opposite.move(left=self.frame.centerx + 75, centery=self.text_time_opposite.centery)
        self.text_money_distance.move(left=self.img_green_arrow_distance.right + 20, centery=self.text_distance.centery)
        self.text_money_time_100.move(left=self.img_green_arrow_time_100.right + 20, centery=self.text_time_100.centery)
        self.text_money_time_opposite.move(left=self.img_green_arrow_time_opposite.right + 20, centery=self.text_time_opposite.centery)
        self.total_money.move(centerx=self.frame.centerx, bottom=self.frame.bottom - 10)

        self.menu_buttons.move(centerx=self.centerx, bottom=self.bottom - 50)

    def restart_game(self):
        self.master.restart_game()
        self.stop()

    def return_to_garage(self):
        self.master.go_to_garage = True
        self.master.stop()
        self.stop()

    def return_to_menu(self):
        self.master.stop()
        self.stop()

class Gameplay(Window):
    def __init__(self, car_id: int, env: Dict[str, Union[str, tuple]]):
        Window.__init__(self, bg_color=env["color"], bg_music=AUDIO["gameplay"])
        self.bind_key(pygame.K_ESCAPE, lambda event: self.pause())
        self.bind_joystick_button(0, "START", lambda event: self.pause())

        font = FONT["cooperblack"]

        # Demaraction lines
        self.road = DrawableListVertical(bg_color=GRAY, offset=70)
        self.white_bands = list()
        self.white_bands_pos = list()
        white_bands_width = 50 #px
        white_lines_height = 10 #px
        for i in range(5):
            if i % 2 == 0:
                self.road.add_object(RectangleShape(self.width, white_lines_height, WHITE))
            else:
                white_bands = DrawableListHorizontal(offset=20)
                while white_bands.width < self.width:
                    white_bands.add_object(RectangleShape(white_bands_width, white_lines_height, WHITE))
                self.road.add_object(white_bands)
                self.white_bands.append(white_bands)

        # Environment
        self.env_up = DrawableListHorizontal(offset=400)
        self.env_down = DrawableListHorizontal(offset=400)
        self.env_limits = [(0, 0), (0, 0)]
        while self.env_up.width < self.width:
            self.env_up.add_object(Image(env["img"], height=110))
        while self.env_down.width < self.width:
            self.env_down.add_object(Image(env["img"], height=110))

        #Infos
        params_for_infos = {
            "font": (font, 45),
            "color": YELLOW,
            "shadow_x": 3,
            "shadow_y": 3
        }
        self.infos_score = Info("Score", round_n=0, **params_for_infos)
        self.infos_speed = Info("Speed", extension="km/h", **params_for_infos, justify="right")
        self.infos_distance = Info("Distance", extension="km", **params_for_infos, justify="right")
        self.infos_time_100 = Info("High speed", **params_for_infos)
        self.infos_time_opposite = Info("Opposite side", **params_for_infos)
        self.clock_time_100 = Clock()
        self.clock_time_opposite = Clock()
        self.total_time_100 = self.total_time_opposite = 0

        self.car = PlayerCar(car_id)
        self.speed = 0
        self.traffic = list()
        self.clock_traffic = Clock()
        self.img_crash = Image(IMG["crash"], size=150)
        self.count_down = CountDown(self, 3, (font, 90), YELLOW, shadow_x=5, shadow_y=5)

        # Default values
        self.update_clock = Clock()
        self.update_time = 10 #ms
        self.pixel_per_sec = 10 # For 1km/h
        self.pixel_per_ms = self.pixel_per_sec * self.update_time / 1000
        self.paused = False
        self.go_to_garage = False
        self.crashed_car = None

        self.disable_key_joy_focus()
        self.init_game()

    def pause(self):
        self.paused = True
        for car in self.traffic + [self.car]:
            car.stop_animation(reset=False)
        pause = Pause(self)
        pause.mainloop()
        if self.loop and not self.count_down.is_shown():
            self.count_down.start(at_end=self.return_to_game)
            self.set_object_priority(self.count_down, self.end_list)

    def return_to_game(self):
        self.paused = False
        for car in self.traffic + [self.car]:
            car.start_animation(loop=True)

    def init_game(self):
        self.go_to_garage = False
        self.paused = False
        self.crashed_car = None
        for info in [self.infos_speed, self.infos_score, self.infos_distance, self.infos_time_100, self.infos_time_opposite]:
            info.value = 0
        for info in [self.infos_time_100, self.infos_time_opposite]:
            info.hide()
        self.total_time_100 = self.total_time_opposite = 0
        self.count_down.start()
        self.img_crash.hide()

    def place_objects(self):
        self.count_down.center = self.road.center = self.center
        self.infos_score.move(topleft=(10, 10))
        self.infos_speed.move(right=self.right - 10, top=10)
        self.infos_distance.move(right=self.right - 10, bottom=self.road.top - 10)
        self.infos_time_100.move(left=10, bottom=self.road.top - 10)
        self.infos_time_opposite.move(left=10, top=self.road.bottom + 10)
        self.car.move(centery=self.road.centery, left=50)
        self.env_up.move(centerx=self.centerx, centery=self.centery * 0.5)
        self.env_down.move(centerx=self.centerx, centery=self.centery * 1.5)

    def update(self):
        if self.paused:
            return
        self.update_player_car()
        if self.update_clock.elapsed_time(self.update_time):
            self.update_infos()
            self.update_background()
            self.update_traffic()

    def update_player_car(self):
        if not self.count_down.is_shown():
            joystick = self.joystick[0]
            controls = SAVE["controls"]
            car_handling = (
                (controls["speed_up"], self.car.speed_up),
                (controls["brake"], self.car.brake),
                (controls["up"], self.car.moveUp),
                (controls["down"], self.car.moveDown),
            )
            for control, car_function in car_handling:
                if self.keyboard.is_pressed(control["key"]):
                    car_function()
                elif joystick[control["joy"]]:
                    car_function(joystick[control["joy"]])
            if SAVE["auto_acceleration"] is True:
                self.car.speed_up()
        self.car.update(self.pixel_per_ms)
        if self.car.top < self.road[0].bottom + 5:
            self.car.top = self.road[0].bottom + 5
        elif self.car.bottom > self.road[-1].top - 5:
            self.car.bottom = self.road[-1].top - 5
        if not self.car.is_crashed():
            self.speed = self.car.speed
            for car in self.traffic:
                collision = pygame.sprite.collide_mask(self.car, car)
                if collision:
                    self.car.crash(car)
                    self.crashed_car = car
                    self.play_sound(AUDIO["crash"])
                    self.img_crash.show()
                    self.img_crash.move(centerx=collision[0] + self.car.left, centery=collision[1] + self.car.top)
                    self.set_object_priority(self.img_crash, self.end_list)
        elif self.car.right <= 0 and self.crashed_car.right <= 0:
            self.end_game()

    def car_in_opposite_side(self) -> bool:
        return bool(self.car.bottom < self.road.centery)

    def update_infos(self):
        if self.car.speed > 0 and self.car_in_opposite_side():
            self.infos_time_opposite.show()
            self.infos_time_opposite.value = self.clock_time_opposite.get_elapsed_time() / 1000
        else:
            self.total_time_opposite += self.infos_time_opposite.value
            self.infos_time_opposite.value = 0
            self.clock_time_opposite.restart()
            self.infos_time_opposite.hide()
        if self.car.speed >= 100:
            self.infos_time_100.show()
            self.infos_time_100.value = self.clock_time_100.get_elapsed_time() / 1000
        else:
            self.total_time_100 += self.infos_time_100.value
            self.infos_time_100.value = 0
            self.clock_time_100.restart()
            self.infos_time_100.hide()
        if self.car.speed > 30:
            score_to_add = 1
            bonus = [
                (self.infos_time_100, 150),
                (self.infos_time_opposite, 120)
            ]
            for info, bonus_points in bonus:
                if info.is_shown():
                    score_to_add += bonus_points * self.update_time / 1000
            if score_to_add > 1:
                self.infos_score.set_color(GREEN_DARK)
                self.infos_score.shadow_color = YELLOW
            else:
                self.infos_score.set_color(YELLOW)
                self.infos_score.shadow_color = BLACK
            self.infos_score.value += score_to_add
        self.infos_speed.value = round(self.car.speed)
        self.infos_distance.value += self.car.speed * self.pixel_per_ms / 1000

    def update_background(self):
        offset = self.speed * self.pixel_per_ms
        for white_bands_list in self.white_bands:
            for band in white_bands_list:
                band.move_ip(-offset, 0)
            band = white_bands_list[0]
            if band.right <= 0:
                white_bands_list.remove_object(band, update_pos=False)
            band = white_bands_list[-1]
            if band.right < self.right:
                white_bands_list.add_object(RectangleShape(*band.size, WHITE), update_pos=False)
        for env in (self.env_up, self.env_down):
            for img in env:
                img.move_ip(-offset, 0)
            img = env[0]
            if img.right <= 0:
                env.remove_object(img, update_pos=False)
                env.add_object(img, update_pos=False)
        if self.img_crash.is_shown():
            self.img_crash.move_ip(-offset, 0)

    def update_traffic(self):
        ways = [list() for _ in range(4)]
        for car in self.traffic.copy():
            car.update(self.speed, self.pixel_per_ms)
            if car.right < 0:
                self.remove_car_from_traffic(car)
            else:
                ways[car.way].append(car)
        for way, car_list in enumerate(ways, 1):
            for i in range(1, len(car_list)):
                car_1 = car_list[i - 1]
                car_2 = car_list[i]
                if car_2.left - car_1.right < 20:
                    if (way in [1, 2]) and (car_1.speed < car_2.speed):
                        car_2.speed = car_1.speed
                    elif (way in [3, 4]) and (car_1.speed > car_2.speed):
                        car_1.speed = car_2.speed
        ratio = (-(self.car.speed / 250) + 2.12) * 1000
        if self.car.speed > 30 and self.clock_traffic.elapsed_time(ratio) and (len(self.traffic) == 0 or self.traffic[-1].right < self.right - 20):
            self.add_car_to_traffic()

    def add_car_to_traffic(self):
        ways = list(range(4))
        score = round(self.infos_score.value)
        nb_cars_to_add = 1
        for threshold in [5000, 12500]:
            if score >= threshold:
                nb_cars_to_add += 1
        for _ in range(nb_cars_to_add):
            car = TrafficCar(random.randint(1, 4), random.choice(ways))
            self.traffic.append(car)
            self.add(car)
            centery = (self.road[car.way].bottom + self.road[car.way + 1].top) / 2
            car.move(left=self.right, centery=centery)
            car.start_animation(loop=True)
            ways.remove(car.way)

    def remove_car_from_traffic(self, car: TrafficCar):
        if car in self.traffic:
            self.traffic.remove(car)
            self.remove(car)

    def end_game(self):
        for car in self.traffic:
            car.stop_animation(reset=False)
        score = round(self.infos_score.value)
        distance = round(self.infos_distance.value, 1)
        time_100 = round(self.total_time_100, 1)
        time_opposite = round(self.total_time_opposite, 1)
        window = EndGame(self, score, distance, time_100, time_opposite)
        window.mainloop()

    def restart_game(self):
        self.init_game()
        self.car.restart()
        for car in self.traffic.copy():
            self.remove_car_from_traffic(car)
        self.place_objects()