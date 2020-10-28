# -*- coding: Utf-8 -*

import os
import pygame
from math import sqrt
from ..window import Window, RESOURCES
from ..path import set_constant_directory, set_constant_file
from ..list import DrawableListVertical
from ..classes import Text, Image, CircleShape
from ..colors import WHITE, BLACK
from ..joystick import Joystick

# Dossiers
img_folder = set_constant_directory("my_pygame", "gamepad_viewer", "files")

# Images
manette_xbox = dict()
for element in reversed(os.listdir(img_folder)):
    if element.endswith(".png") and element.startswith("xbox") and "contour" not in element:
        i = int(element[5])
        button = element[7:-4] if element[7:-4] != "" else None
        if i not in manette_xbox:
            manette_xbox[i] = dict()
        manette_xbox[i][button] = set_constant_file(img_folder, element)
    else:
        continue
RESOURCES.IMG = manette_xbox

class Gamepad(Image):

    def __init__(self, joystick: Joystick, gamepad_dict: dict, index: int):
        Image.__init__(self, gamepad_dict[index][None])
        self.joystick = joystick
        self.index = index
        self.gamepad_dict = gamepad_dict[index]
        self.gamepad_dict.pop(None, None)

    def after_drawing(self, surface: pygame.Surface) -> None:
        for button, img in self.gamepad_dict.items():
            if self.joystick[button]:
                surface.blit(img, self.rect)
        if self.index == 1:
            self.draw_circle_axis(surface)

    def draw_circle_axis(self, surface: pygame.Surface):
        w, h = s = self.size

        joystick = {"LEFT": {"x": 0, "y": 0}, "RIGHT": {"x": 0, "y": 0}}
        axis_center = {"LEFT": (0, 0), "RIGHT": (0, 0)}

        joystick["LEFT"]["x"], joystick["LEFT"]["y"]  = round(0.255 * w), round(0.306 * h)
        joystick["RIGHT"]["x"], joystick["RIGHT"]["y"] = round(0.631 * w), round(0.528 * h)

        surface_for_axis = pygame.Surface(s, pygame.SRCALPHA)
        surface_for_axis.fill((0,0,0,0))

        circle_size = round(0.151 * w)
        circle_radius = round(0.151 * w / 2)

        radius = round(0.70 * circle_size / 2)
        r = circle_radius  - round(radius / 2)

        for side in joystick:
            h = joystick[side]["x"]
            k = joystick[side]["y"]
            x = a = self.joystick[f"AXIS_{side}_X"]*r + h
            y = b = self.joystick[f"AXIS_{side}_Y"]*r + k
            if (a-h)**2 + (b-k)**2 > r**2:
                x = h + (r*(a-h))/sqrt((a-h)**2 + (b-k)**2)
                y = k + (r*(b-k))/sqrt((a-h)**2 + (b-k)**2)

            axis_center[side] = round(x), round(y)

        for side, button in (("LEFT", "L3"), ("RIGHT", "R3")):
            circle = CircleShape(radius, WHITE, outline=1)
            intern_circle = CircleShape(round(0.704*radius), BLACK if self.joystick[button] else None, outline=1)
            circle.center = intern_circle.center = axis_center[side]
            circle.draw(surface_for_axis)
            intern_circle.draw(surface_for_axis)

        surface.blit(surface_for_axis, self.rect)

class CalibrateJoystick(Window):
    def __init__(self, master):
        Window.__init__(self, bg_color=master.bg_color)
        self.disable_key_joy_focus()

        self.font = font = (pygame.font.get_default_font(), 30)
        options = [
            "S: Passer",
            "A: Retour en arrière",
            "Q: Quitter"
        ]
        self.topleft_options = Text("\n".join(options), font)
        self.instruction = Text(font=font)
        self.joy_key = Text(font=font)
        self.validated = Text("Validated", font=font)
        self.validated.hide()

        self.joy_buttons = ["A", "B", "X", "Y", "L1", "R1", "SELECT", "START"]
        self.joy_triggers = ["L2", "R2"]
        self.joy_thumbs = ["L3", "R3"]
        self.joy_dpad = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.joy_axis = ["AXIS_LEFT_X", "AXIS_LEFT_Y", "AXIS_RIGHT_X", "AXIS_RIGHT_Y"]
        self.joy = self.joy_buttons + self.joy_triggers + self.joy_thumbs + self.joy_dpad + self.joy_axis

        self.index = 0
        self.update_instructions()

        self.bind_key(pygame.K_s, lambda key: self.next_joy())
        self.bind_key(pygame.K_a, lambda key: self.previous_joy())
        self.bind_key(pygame.K_q, lambda key: self.stop())
        for event in (pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYHATMOTION):
            self.bind_event(event, self.calibration_event)

    def set_grid(self):
        self.topleft_options.move(left=10, top=10)
        self.instruction.move(y=250, centerx=self.centerx)
        self.joy_key.move(top=self.instruction.bottom, centerx=self.instruction.centerx)
        self.validated.move(top=self.joy_key.bottom, centerx=self.instruction.centerx)

    def previous_joy(self):
        if self.validated.is_shown():
            return
        if self.index > 0:
            self.index -= 1
            self.update_instructions()

    def next_joy(self, after_validation=False):
        if after_validation:
            self.validated.hide()
        if self.validated.is_shown():
            return
        self.index += 1
        if self.index == len(self.joy):
            self.stop()
        else:
            self.update_instructions()

    def update_instructions(self):
        if self.joy[self.index] in self.joy_buttons + self.joy_triggers:
            self.instruction.message = "Appuyer sur le bouton :"
            self.joy_key.message = self.joy[self.index]
        elif self.joy[self.index] in self.joy_thumbs:
            self.instruction.message = "Appuyer sur le joystick {} :".format("gauche" if self.joy[self.index] == "L3" else "droit")
            self.joy_key.message = self.joy[self.index]
        elif self.joy[self.index] in self.joy_dpad:
            self.instruction.message = "Appuyer sur la flèche :"
            self.joy_key.message = {"UP": "HAUT", "DOWN": "BAS", "LEFT": "GAUCHE", "RIGHT": "DROITE"}[self.joy[self.index]]
        elif self.joy[self.index] in self.joy_axis:
            cote, sens = self.joy[self.index].split("_")[1:]
            self.instruction.message = "Faire bouger le joystick {} {} :".format("gauche" if cote == "LEFT" else "droit", "horizontalement" if sens == "X" else "verticalement")
            self.joy_key.message = str()

    def calibration_event(self, event: pygame.event.Event):
        if self.validated.is_shown():
            return
        valid = False
        if event.type == pygame.JOYBUTTONDOWN and event.instance_id == self.joystick[0].id:
            self.joystick[0].set_event(self.joy[self.index], event.type, event.button)
            valid = True
        elif event.type == pygame.JOYAXISMOTION and event.instance_id == self.joystick[0].id and abs(event.value) > 0.9:
            self.joystick[0].set_event(self.joy[self.index], event.type, event.axis)
            valid = True
        elif event.type == pygame.JOYHATMOTION and event.instance_id == self.joystick[0].id:
            if (event.value[0] == 0 and event.value[1] != 0) or (event.value[0] != 0 and event.value[1] == 0):
                self.joystick[0].set_event(self.joy[self.index], event.type, event.hat, hat_value=event.value)
                valid = True
        if valid:
            self.validated.show()
            self.after(1000, lambda: self.next_joy(after_validation=True))

class GamepadViewer(Window):
    def __init__(self):
        Window.__init__(self, size=(800, 600), bg_color=WHITE)
        if self.main_window:
            self.set_title("Diagnostic manettes")
        self.set_joystick(1)
        self.disable_key_joy_focus()

        self.font = font = (pygame.font.get_default_font(), 20)
        self.config_fps_obj(font=font, color=BLACK)

        options = [
            "E: Etalonner"
        ]
        self.topleft_options = Text("\n".join(options), font)
        self.connected_gamepad_title = Text("Liste des manettes connectées", font)
        self.connected_gamepad = DrawableListVertical(offset=0)

        self.gamepad_1 = Gamepad(self.joystick[0], RESOURCES.IMG, 1)
        self.gamepad_2 = Gamepad(self.joystick[0], RESOURCES.IMG, 2)

        self.bind_key(pygame.K_e, lambda key: CalibrateJoystick(self).mainloop())

    def place_objects(self):
        self.move_fps_object(top=10, right=self.right)
        self.topleft_options.move(left=10, top=10)
        self.connected_gamepad_title.move(left=self.topleft_options.left, top=self.topleft_options.bottom + 30)
        self.gamepad_1.move(bottom=self.bottom - 10, right=self.right - 10)
        self.gamepad_2.move(bottom=self.gamepad_1.top - 20, centerx=self.gamepad_1.centerx)

    def update(self):
        self.connected_gamepad.clear()
        for i, nom in enumerate(Joystick.list()):
            self.connected_gamepad.add(Text(" {} {}".format(">" if i == 0 else " ", nom), self.font))
        self.connected_gamepad.move(left=self.connected_gamepad_title.left, top=self.connected_gamepad_title.bottom)