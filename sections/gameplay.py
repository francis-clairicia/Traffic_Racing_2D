# -*- coding: Utf-8 -*

import random
from typing import Dict, List, Union, Iterator
import pygame
from my_pygame import Window, Drawable, RectangleShape, Text, Image, Button
from my_pygame import DrawableList, DrawableListHorizontal, DrawableListVertical
from my_pygame import ButtonListHorizontal, ButtonListVertical
from my_pygame import Sprite, CountDown, Clock
from my_pygame import GRAY, WHITE, BLACK, YELLOW, GREEN, GREEN_LIGHT, GREEN_DARK
from constants import RESOURCES, ENVIRONMENT, CAR_INFOS, NB_TRAFFIC_CARS
from save import SAVE
from .options import Options

def format_number(number: float) -> str:
    return f"{number:,}".replace(",", " ")

class Car(Sprite):
    def __init__(self, img_list):
        Sprite.__init__(self)
        self.add_sprite_list("car", img_list, set_sprite_list=True, height=55)
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
            self.stop_animation()

class PlayerCar(Car):
    def __init__(self, car_id: int):
        Car.__init__(self, RESOURCES.IMG["gameplay_cars"][car_id])

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

    def update(self, pixel_per_ms: int):
        if not self.__crashed and self.__speed_clock.elapsed_time(self.__speed_time):
            if self.__braking:
                self.speed -= (self.__speed_time * self.max_speed / self.braking) * self.__braking_offset
                if self.speed < 30:
                    self.speed = 30
            elif self.__speed_up:
                self.speed += (self.__speed_time * 100 / self.acceleration) * self.__speed_up_offset
            else:
                ratio = 10 # percent
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

    def speed_up(self, offset: int):
        if not self.__speed_up and offset > 0:
            self.__speed_up = True
            self.__speed_up_offset = offset

    def brake(self, offset: int):
        if not self.__braking and offset > 0:
            self.__braking = True
            self.__braking_offset = offset

    def moveUp(self, offset: int):
        if not self.__move and offset > 0:
            self.__move = True
            self.__move_offset = -offset

    def moveDown(self, offset: int):
        if not self.__move and offset > 0:
            self.__move = True
            self.__move_offset = offset

class TrafficCar(Car):
    def __init__(self, sprites_traffic_cars: dict, car_id: int, way: int):
        side = "opposé" if way in [0, 1] else "normal"
        Car.__init__(self, sprites_traffic_cars[side][car_id])
        self.way = way
        self.side = 1 if side == "normal" else -1
        self.speed = (35, 40, 50, 60)[car_id - 1]

    def update(self, pixel_per_ms: int):
        x = (self.speed * self.side) * pixel_per_ms
        self.move_ip(x, 0)

class TrafficCarList(DrawableList):
    def __init__(self, nb_ways: int, max_nb_car: int):
        DrawableList.__init__(self)
        self.sprites_traffic_cars = dict()
        for side, car_list in RESOURCES.IMG["traffic"].items():
            self.sprites_traffic_cars[side] = dict()
            for car_id, img_list in car_list.items():
                self.sprites_traffic_cars[side][car_id] = img_list
        self.nb_ways = nb_ways
        self.max_nb_car = max_nb_car

    def add_cars(self, master: Window, road: DrawableListVertical, score: int) -> None:
        ways = list(range(self.nb_ways))
        nb_cars_to_add = 1
        for threshold in (5000, 12500):
            if score >= threshold:
                nb_cars_to_add += 1
            else:
                break
        for _ in range(nb_cars_to_add):
            if len(self) >= self.max_nb_car:
                break
            car = TrafficCar(self.sprites_traffic_cars, random.randint(1, NB_TRAFFIC_CARS), random.choice(ways))
            car.move(left=master.right, centery=(road[car.way].bottom + road[car.way + 1].top) / 2)
            car.start_animation(loop=True)
            self.add(car)
            ways.remove(car.way)

    def way(self, index: int) -> Iterator[TrafficCar]:
        return filter(lambda car: car.way == index, self.drawable)

    @property
    def ways(self) -> List[List[TrafficCar]]:
        return [list(self.way(i + 1)) for i in range(self.nb_ways)]

    @property
    def last(self) -> TrafficCar:
        return max(self.drawable, key=lambda car: car.right, default=None)

class Info(Text):
    def __init__(self, title: str, extension="", round_n=1, **kwargs):
        Text.__init__(self, **kwargs)
        self.__title = title
        self.__extension = extension
        self.__round_n = round_n
        self.__clock = Clock()
        self.value = 0

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("value must be an integer or a float")
        self.__value = value
        if self.__clock.elapsed_time(200):
            if self.__round_n:
                value_format = "{" + ":.{n}f".format(n=self.__round_n) + "}"
                value = value_format.format(value)
            else:
                value = str(round(value))
            msg = self.__title + "\n" + value
            if len(self.__extension) > 0:
                msg += " " + self.__extension
            self.message = msg

class Pause(Window):
    def __init__(self, master):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())
        self.bind_joystick(0, "START", lambda event: self.stop())
        self.bind_joystick(0, "B", lambda event: self.stop())
        self.master = master
        self.bg = RectangleShape(*self.size, (0, 0, 0, 170))
        params_for_all_buttons = {
            "font": (RESOURCES.FONT["algerian"], 100),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "hover_sound": RESOURCES.SFX["select"],
            "on_click_sound": RESOURCES.SFX["validate"],
            "outline": 3,
            "highlight_color": YELLOW
        }
        self.menu_buttons = ButtonListVertical(offset=30)
        self.menu_buttons.add(
            Button(self, "Return", **params_for_all_buttons, callback=self.stop),
            Button(self, "Options", **params_for_all_buttons, callback=self.show_options),
            Button(self, "Garage", **params_for_all_buttons, callback=self.return_to_garage),
            Button(self, "Menu", **params_for_all_buttons, callback=self.return_to_menu)
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
        self.text_score = Text(f"Your score\n{score}", (RESOURCES.FONT["algerian"], 90), YELLOW, justify="center")
        self.img_highscore = Image(RESOURCES.IMG["new_high_score"], width=150)
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
        self.text_money = Text(format_number(SAVE["money"]), (RESOURCES.FONT["algerian"], 50), YELLOW, img=Image(RESOURCES.IMG["piece"], height=40), compound="right")

        font = ("calibri", 50)
        self.frame = RectangleShape(0.75 * self.width, 0.45 * self.height, BLACK, outline=1, outline_color=WHITE)
        self.text_distance = Text(f"Distance: {distance}", font, WHITE)
        self.img_green_arrow_distance = Image(RESOURCES.IMG["green_arrow"], height=40)
        self.text_money_distance = Text(money_distance, font, WHITE, img=Image(RESOURCES.IMG["piece"], height=40), compound="right")
        self.text_time_100 = Text(f"Time up to 100: {time_100}", font, WHITE)
        self.img_green_arrow_time_100 = Image(RESOURCES.IMG["green_arrow"], height=40)
        self.text_money_time_100 = Text(money_time_100, font, WHITE, img=Image(RESOURCES.IMG["piece"], height=40), compound="right")
        self.text_time_opposite = Text(f"Time in opposite side: {time_opposite}", font, WHITE)
        self.img_green_arrow_time_opposite = Image(RESOURCES.IMG["green_arrow"], height=40)
        self.text_money_time_opposite = Text(money_time_opposite, font, WHITE, img=Image(RESOURCES.IMG["piece"], height=40), compound="right")
        self.total_money = DrawableListHorizontal(offset=10)
        self.total_money.add(
            Text("TOTAL: ", font, WHITE),
            Text(money_gained, font, WHITE, img=Image(RESOURCES.IMG["piece"], height=40), compound="right")
        )

        params_for_all_buttons = {
            "font": (RESOURCES.FONT["algerian"], 50),
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "hover_sound": RESOURCES.SFX["select"],
            "on_click_sound": RESOURCES.SFX["validate"],
            "outline": 3,
            "highlight_color": YELLOW
        }
        self.menu_buttons = ButtonListHorizontal(offset=30)
        self.menu_buttons.add(
            Button(self, "Restart", **params_for_all_buttons, callback=self.restart_game),
            Button(self, "Garage", **params_for_all_buttons, callback=self.return_to_garage),
            Button(self, "Menu", **params_for_all_buttons, callback=self.return_to_menu)
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
        self.master.restart = True
        self.stop()

    def return_to_garage(self):
        self.master.go_to_garage = True
        self.master.stop()
        self.stop()

    def return_to_menu(self):
        self.master.stop()
        self.stop()

class Gameplay(Window):
    def __init__(self, car_id: int, env: str):
        Window.__init__(self, bg_color=ENVIRONMENT[env], bg_music=RESOURCES.MUSIC["gameplay"])
        self.bind_key(pygame.K_ESCAPE, lambda event: self.pause())
        self.bind_joystick(0, "START", lambda event: self.pause())

        font = RESOURCES.FONT["cooperblack"]

        # Demaraction lines
        self.road = DrawableListVertical(bg_color=GRAY, offset=70)
        self.white_bands = list()
        white_bands_width = 50 #px
        white_lines_height = 10 #px
        for i in range(5):
            if i % 2 == 0:
                self.road.add(RectangleShape(self.width, white_lines_height, WHITE))
            else:
                white_bands = DrawableListHorizontal(offset=20)
                while white_bands.width < self.width:
                    white_bands.add(RectangleShape(white_bands_width, white_lines_height, WHITE))
                self.road.add(white_bands)
                self.white_bands.append(white_bands)

        # Environment
        self.env_top = DrawableListHorizontal(offset=400)
        self.env_bottom = DrawableListHorizontal(offset=400)
        while self.env_top.width < self.width:
            self.env_top.add(Image(RESOURCES.IMG[env], height=110))
        while self.env_bottom.width < self.width:
            self.env_bottom.add(Image(RESOURCES.IMG[env], height=110))

        #Infos
        params_for_infos = {
            "font": (font, 45),
            "color": YELLOW,
            "shadow": True,
            "shadow_x": 3,
            "shadow_y": 3
        }
        self.infos_score = Info("Score", round_n=0, **params_for_infos)
        self.infos_speed = Info("Speed", extension="km/h", **params_for_infos, justify="right")
        self.infos_distance = Info("Distance", round_n=2, extension="km", **params_for_infos, justify="right")
        self.infos_time_100 = Info("High speed", **params_for_infos)
        self.infos_time_opposite = Info("Opposite side", **params_for_infos)
        self.clock_time_100 = Clock()
        self.clock_time_opposite = Clock()
        self.total_time_100 = self.total_time_opposite = 0

        self.car = PlayerCar(car_id)
        self.speed = 0
        self.traffic = TrafficCarList(nb_ways=4, max_nb_car=6)
        self.clock_traffic = Clock()
        self.img_crash = Image(RESOURCES.IMG["crash"], size=150)
        self.count_down = CountDown(self, 3, font=(font, 90), color=YELLOW, shadow=True, shadow_x=5, shadow_y=5)
        self.last_car_way = 0

        # Background
        self.background = DrawableList(draw=False)
        self.background.add(
            self.env_top,
            self.env_bottom,
            *self.white_bands,
            self.traffic
        )

        # Default values
        self.update_clock = Clock()
        self.update_time = 15 #ms
        self.pixel_per_sec = 6 # For 1km/h
        self.pixel_per_ms = self.pixel_per_sec * self.update_time / 1000
        self.paused = False
        self.go_to_garage = self.restart = False
        self.crashed_car = None

        self.disable_key_joy_focus()
        self.init_game()

    def pause(self):
        if not self.count_down.is_shown():
            self.paused = True
            self.car.stop_animation()
            for car in self.traffic:
                car.stop_animation()
        pause = Pause(self)
        pause.mainloop()
        if self.loop and not self.count_down.is_shown():
            self.count_down.start(at_end=self.return_to_game)
            self.objects.set_priority(self.count_down, self.objects.end)

    def return_to_game(self):
        self.paused = False
        self.car.restart_animation()
        for car in self.traffic:
            car.restart_animation()
        self.clock_traffic.tick()
        self.clock_time_100.tick()
        self.clock_time_opposite.tick()
        self.update_clock.tick()

    def init_game(self):
        self.go_to_garage = False
        self.paused = False
        self.crashed_car = None
        for info in (self.infos_speed, self.infos_score, self.infos_distance, self.infos_time_100, self.infos_time_opposite):
            info.value = 0
            if info in (self.infos_time_100, self.infos_time_opposite):
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
        self.env_top.move(centerx=self.centerx, centery=(self.top + self.road[0].top) / 2)
        self.env_bottom.move(centerx=self.centerx, centery=(self.road[-1].bottom + self.bottom) / 2)

    def update(self):
        if self.paused:
            return
        self.update_player_car()
        if self.update_clock.elapsed_time(self.update_time):
            self.update_infos()
            self.update_background()
            self.update_traffic()
            self.rect_to_update = (
                self.road.rect, self.env_top.rect, self.env_bottom.rect,
                self.infos_score.rect, self.infos_speed.rect, self.infos_distance.rect,
                self.infos_time_100.rect, self.infos_time_opposite.rect
            )

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
                car_function(self.keyboard.is_pressed(control["key"]))
                car_function(joystick.get_value(control["joy"]))
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
                    self.play_sound(RESOURCES.SFX["crash"])
                    self.img_crash.show()
                    self.img_crash.move(centerx=collision[0] + self.car.left, centery=collision[1] + self.car.top)
                    self.objects.set_priority(self.img_crash, self.objects.end)
        elif self.car.right <= 0 and self.crashed_car.right <= 0:
            self.end_game()

    def car_in_opposite_side(self) -> bool:
        return bool(self.car.bottom < self.road.centery)

    def update_infos(self):
        min_speed = 30
        score_to_add = (self.car.speed - min_speed) / 5
        bonus = False
        if self.car.speed > 30 and self.car_in_opposite_side():
            self.infos_time_opposite.show()
            self.infos_time_opposite.value = self.clock_time_opposite.get_elapsed_time() / 1000
            score_to_add += 120
            bonus = True
        else:
            self.total_time_opposite += self.infos_time_opposite.value
            self.infos_time_opposite.value = 0
            self.clock_time_opposite.restart()
            self.infos_time_opposite.hide()
        if self.car.speed >= 100:
            self.infos_time_100.show()
            self.infos_time_100.value = self.clock_time_100.get_elapsed_time() / 1000
            score_to_add += 150
            bonus = True
        else:
            self.total_time_100 += self.infos_time_100.value
            self.infos_time_100.value = 0
            self.clock_time_100.restart()
            self.infos_time_100.hide()
        if bonus:
            self.infos_score.color = GREEN_DARK
            self.infos_score.shadow_color = YELLOW
        else:
            self.infos_score.color = YELLOW
            self.infos_score.shadow_color = BLACK
        self.infos_score.value += score_to_add * self.update_time / 1000
        self.infos_speed.value = self.car.speed
        self.infos_distance.value += self.car.speed * self.pixel_per_ms / (1000 * 3.6)

    def update_background(self):
        offset = self.speed * self.pixel_per_ms
        self.background.move_ip(-offset, 0)
        for white_bands_list in self.white_bands:
            if white_bands_list[0].right <= 0:
                white_bands_list.remove_from_index(0)
            if white_bands_list[-1].right < self.right:
                white_bands_list.add(RectangleShape(*white_bands_list[-1].size, WHITE))
        for env in (self.env_top, self.env_bottom):
            img = env[0]
            if img.right <= 0:
                img.move(left=env[-1].right + env.offset)
                env.set_priority(img, env.end)
        if self.img_crash.is_shown():
            self.img_crash.move_ip(-offset, 0)

    def update_traffic(self):
        for car in self.traffic.drawable:
            car.update(self.pixel_per_ms)
            if car.right < 0:
                self.traffic.remove(car)
        for way, car_list in enumerate(self.traffic.ways, 1):
            for i in range(1, len(car_list)):
                car_1 = car_list[i - 1]
                car_2 = car_list[i]
                if car_2.left - car_1.right < 20:
                    if (way in [1, 2]) and (car_1.speed < car_2.speed):
                        car_2.speed = car_1.speed
                    elif (way in [3, 4]) and (car_1.speed > car_2.speed):
                        car_1.speed = car_2.speed
        ratio = (2 - (round(self.infos_score.value) / 20000)) * 1000
        if self.car.speed > 30 and self.clock_traffic.elapsed_time(ratio):
            if self.traffic.empty() or self.traffic.last.right < self.right - 20:
                self.traffic.add_cars(self, self.road, round(self.infos_score.value))

    def end_game(self):
        for car in self.traffic:
            car.stop_animation()
        self.crashed_car = None
        score = round(self.infos_score.value)
        distance = round(self.infos_distance.value, 1)
        time_100 = round(self.total_time_100, 1)
        time_opposite = round(self.total_time_opposite, 1)
        window = EndGame(self, score, distance, time_100, time_opposite)
        window.mainloop()
        if self.restart:
            self.traffic.clear()
            self.car.move(left=50, centery=self.road.centery)
            self.car.restart()
            self.init_game()