# -*- coding: Utf-8 -*

import sys
import pygame
from sections.garage import Garage
from sections.options import Options
from my_pygame import Window, Image, Button, RectangleShape, Text, ImageButton
from my_pygame import ButtonListVertical
from my_pygame import GREEN, GREEN_DARK, GREEN_LIGHT, YELLOW
from my_pygame import RESOURCES
from constants import ICON
from save import SAVE

class Credits(Window):
    def __init__(self, master: Window):
        Window.__init__(self, master=master, bg_music=master.bg_music)
        self.frame = RectangleShape(0.60 * self.width, 0.60 * self.height, GREEN, outline=3)
        title_font = ("calibri", 32, "bold")
        simple_font = ("calibri", 32)
        self.all_text = all_text = list()
        all_text.append(Text("Backgroun musics", title_font))
        all_text.append(Text("by Eric Matyas: www.soundimage.org", simple_font))
        all_text.append(Text("SFX", title_font))
        all_text.append(Text("taken on Freesound.org", simple_font))
        all_text.append(Text("Images", title_font))
        all_text.append(Text("taken in Google Image\n(except the logo)", simple_font, justify=Text.T_CENTER))
        self.objects.add(*all_text)
        self.button_red_cross = ImageButton(self, img=RESOURCES.IMG["red_cross"],
                                            active_img=RESOURCES.IMG["red_cross_hover"],
                                            hover_sound=RESOURCES.SFX["select"], on_click_sound=RESOURCES.SFX["back"],
                                            callback=self.stop, highlight_color=YELLOW)
        self.bind_key(pygame.K_ESCAPE, lambda event: self.stop(sound=self.button_red_cross.on_click_sound))
        self.bind_joystick_button(0, "B", lambda event: self.stop(sound=self.button_red_cross.on_click_sound))

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
        Window.__init__(self, flags=pygame.DOUBLEBUF|pygame.FULLSCREEN, bg_music=RESOURCES.MUSIC["menu"])
        self.set_title("Traffic Racing 2D")
        self.set_icon(ICON)
        self.set_fps(120)
        self.config_fps_obj(font=("calibri", 30))
        self.set_joystick(1)
        self.joystick[0].set_button_axis(False)
        self.bind_key(pygame.K_ESCAPE, lambda key: self.stop())
        self.bg = Image(RESOURCES.IMG["background"], width=self.width)
        self.logo = Image(RESOURCES.IMG["logo"])
        params_for_all_buttons = {
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
            Button(self, "Play", font=(RESOURCES.FONT["algerian"], 100), **params_for_all_buttons, callback=self.goto_garage),
            Button(self, "Options", font=(RESOURCES.FONT["algerian"], 100), **params_for_all_buttons, callback=self.show_options),
            Button(self, "Quit", font=(RESOURCES.FONT["algerian"], 100), **params_for_all_buttons, callback=self.stop)
        )
        self.button_credits = Button(self, "Credits", font=(RESOURCES.FONT["algerian"], 50), **params_for_all_buttons, callback=self.show_credits)

    def on_quit(self):
        SAVE.dump()

    def place_objects(self):
        self.bg.center = self.center
        self.logo.midtop = self.midtop
        self.menu_buttons.center = self.centerx, self.centery + self.menu_buttons[0].height
        self.button_credits.move(bottom=self.bottom - 50, left=self.left + 10)
        self.move_fps_object(top=self.top + 10, centerx=self.centerx)

    def set_grid(self):
        self.menu_buttons.set_obj_on_side(on_left=self.button_credits, on_top=self.button_credits, on_bottom=self.button_credits)
        self.button_credits.set_obj_on_side(on_top=self.menu_buttons[-1], on_bottom=self.menu_buttons[0], on_right=self.menu_buttons[0])

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