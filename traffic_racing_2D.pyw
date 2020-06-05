# -*- coding: Utf-8 -*

import sys
import pygame
from sections.garage import Garage
# from sections.gameplay import *
from sections.options import Options
from my_pygame import Window, Image, Button, RectangleShape, Text, ImageButton
from my_pygame import GREEN, GREEN_DARK, GREEN_LIGHT, BLACK, YELLOW
from constants import IMG, ICON, AUDIO, FONT
from save import SAVE

class Credits(Window):
    def __init__(self, master: Window):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.frame = RectangleShape(0.60 * self.width, 0.60 * self.height, GREEN, outline=3)
        title_font = ("calibri", 32, "bold")
        simple_font = ("calibri", 32)
        self.all_text = all_text = list()
        all_text.append(Text("Backgroun musics", title_font, BLACK))
        all_text.append(Text("by Eric Matyas: www.soundimage.org", simple_font, BLACK))
        all_text.append(Text("SFX", title_font, BLACK))
        all_text.append(Text("taken on Freesound.org", simple_font, BLACK))
        all_text.append(Text("Images", title_font, BLACK))
        all_text.append(Text("taken Google Image\n(except the logo)", simple_font, BLACK, justify=Text.T_CENTER))
        for text in all_text:
            self.add(text)
        self.button_red_cross = ImageButton(self, Image(IMG["red_cross"]),
                                            active_img=Image(IMG["red_cross_hover"]),
                                            hover_sound=AUDIO["select"],
                                            command=self.stop, highlight_color=YELLOW)
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop())
        self.bind_joystick_button(0, "B", lambda event: self.stop())

    def on_quit(self):
        self.play_sound(AUDIO["back"])

    def place_objects(self):
        self.frame.center = self.center
        self.button_red_cross.move(left=self.frame.left + 5, top=self.frame.top + 5)
        for i, text in enumerate(self.all_text):
            if i == 0:
                text.move(centerx=self.frame.centerx, y=self.frame.y + 20)
            else:
                text.move(centerx=self.frame.centerx, y=self.all_text[i - 1].bottom + (40 if text.font.get_bold() else 0))

class TrafficRacing(Window):
    def __init__(self):
        Window.__init__(self, flags=pygame.NOFRAME, bg_music=AUDIO["menu"])
        self.set_title("Traffic Racing 2D")
        self.set_icon(ICON)
        self.set_joystick(1)
        self.bind_key(pygame.K_ESCAPE, lambda key: self.stop())
        self.bg = Image(IMG["background"], width=self.width)
        self.logo = Image(IMG["logo"])
        params_for_all_buttons = {
            "bg": GREEN,
            "hover_bg": GREEN_LIGHT,
            "active_bg": GREEN_DARK,
            "hover_sound": AUDIO["select"],
            "on_click_sound": AUDIO["validate"],
            "outline": 3,
            "highlight_color": YELLOW
        }
        self.button_play = Button(self, "Play", font=(FONT["algerian"], 100), **params_for_all_buttons, command=self.goto_garage)
        self.button_options = Button(self, "Options", font=(FONT["algerian"], 100), **params_for_all_buttons, command=self.show_options)
        self.button_quit = Button(self, "Quit", font=(FONT["algerian"], 100), **params_for_all_buttons, command=self.stop)
        self.button_credits = Button(self, "Credits", font=(FONT["algerian"], 50), **params_for_all_buttons, command=self.show_credits)

    def on_quit(self):
        SAVE.dump()

    def place_objects(self):
        self.bg.center = self.center
        self.logo.midtop = self.midtop
        self.button_play.midbottom = self.center
        self.button_options.move(top=self.button_play.bottom + 30, centerx=self.button_play.centerx)
        self.button_quit.move(top=self.button_options.bottom + 30, centerx=self.button_options.centerx)
        self.button_credits.move(bottom=self.bottom - 50, left=self.left + 10)
        self.show_fps(SAVE["fps"], font=("calibri", 30), bottom=self.bottom - 50, centerx=self.centerx)

    def set_grid(self):
        self.button_play.set_obj_on_side(on_bottom=self.button_options, on_top=self.button_credits, on_left=self.button_credits)
        self.button_options.set_obj_on_side(on_top=self.button_play, on_bottom=self.button_quit, on_left=self.button_credits)
        self.button_quit.set_obj_on_side(on_top=self.button_options, on_bottom=self.button_credits, on_left=self.button_credits)
        self.button_credits.set_obj_on_side(on_top=self.button_quit, on_bottom=self.button_play, on_right=self.button_play)

    def show_options(self):
        self.hide_all(without=[self.bg])
        Options(self).mainloop()
        self.show_all()

    def show_credits(self):
        self.hide_all(without=[self.bg])
        Credits(self).mainloop()
        self.show_all()

    def goto_garage(self):
        Garage().mainloop()

def main():
    game = TrafficRacing()
    game.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(main())