# -*-coding:Utf-8-*

import os
import sys
import time
from threading import Thread
from pickle import Pickler, Unpickler
import pygame
from pygame.locals import *
pygame.init()

class Controller(Thread):
	
	"""Classe pour assurer l'utilisation des manettes"""
	joystick_list = []
	running = False
	name_list = []
	clock = pygame.time.Clock()
	chrono = compteur = 0
	refresh_delay = 0.5 #sec
	time = 0
	
	def __init__(self):
		Controller.joystick_list.append(self)
		
		self.__n = self.id = ""
		
		self.init_gamepad_values()
		self.default_button_axis_dpad()
		
		self.fichier_sauvegarde = os.path.join(sys.path[0], "controller.bin")
		if os.path.isfile(self.fichier_sauvegarde):
			with open(self.fichier_sauvegarde, "rb") as sauvegarde:
				sauvegarde = Unpickler(sauvegarde)
				self.sauvegarde = sauvegarde.load()
		else:
			self.sauvegarde = {}
		
		if not Controller.running:
			Thread.__init__(self)
			self.init_thread()
			print("Controller module initialized")
	
	def init_thread(self):
		self.start()
		pygame.register_quit(self.quit)
		Controller.time = time.time()
	
	def get_init(self):
		return Controller.running
	
	def run(self):
		Controller.running = True
		while Controller.running:
			Controller.clock.tick(60)
			Controller.chrono = time.time() - Controller.time
			self.check_connection()
	
	def check_connection(self):
		if Controller.chrono >= Controller.compteur:
			Controller.compteur += Controller.refresh_delay
			pygame.joystick.quit()
			pygame.joystick.init()
		n = []
		try:
			joystick_list = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
		except pygame.error:
			joystick_list = []
		for j in joystick_list:
			j.init() 
			n.append(j.get_name())
		pygame.time.wait(20)
		for joystick in Controller.joystick_list:
			connected = False
			for joystick_name in n:
				connected = all(word in joystick_name.lower() for word in joystick.id.lower().split())
				if connected:
					break
			if connected:
				joystick.init(joystick_list[n.index(joystick_name)])
			else:
				joystick.init()
		
		Controller.name_list = sorted(n)
	
	def quit(self):
		if Controller.running:
			Controller.running = False
			self.join()
		Controller.chrono = Controller.compteur = 0
	
	@staticmethod
	def list(i=None):
		if type(i) is int:
			return Controller.name_list[i] if i in range(len(Controller.name_list)) else None
		else:
			return Controller.name_list
	
	@staticmethod
	def count():
		return len(Controller.name_list)
	
	"""----------------Utilisation d'une manette------------"""
	
	def init(self, joystick=None):
		if joystick is not None:
			try:
				self.__n = joystick.get_name()
				self.get_gamepad_values(joystick)
				self.load()
			except pygame.error:
				self.init_gamepad_values()
		else:
			self.__n = ""
			self.init_gamepad_values()
	
	def connected(self):
		return bool(len(self.name))
	
	def init_gamepad_values(self):
		self.button_value = {i:0 for i in range(-1, 33)}
		self.axis_value = {i:0 for i in range(-1, 5)}
		self.hat_value = {i:(0, 0) for i in range(-1, 2)}
		
	def get_gamepad_values(self, joystick):
		try:
			for i in range(joystick.get_numaxes()):
				self.axis_value[i] = joystick.get_axis(i)
			for i in range(joystick.get_numbuttons()):
				self.button_value[i] = joystick.get_button(i)
			for i in range(joystick.get_numhats()):
				self.hat_value[i] = joystick.get_hat(i)
		except:
			pass
	
	"""------------------------------------------------------------------"""
	
	def calibrate(self):
		value_list = list(self.boutons_manette.values()) + list(self.axis_manette.values()) + list(self.dpad_manette.values())
		return all(v == -1 for v in value_list)
	
	def default_button_axis_dpad(self):
		self.__button_list = button = ["A", "B", "X", "Y", "L1", "L2", "R1", "R2", "SELECT", "START", "L3", "R3"]
		self.__axis_list = axis = ["AXIS_LEFT_X", "AXIS_LEFT_Y", "AXIS_RIGHT_X", "AXIS_RIGHT_Y"]
		self.__dpad_list = dpad = ["UP", "DOWN", "LEFT", "RIGHT"]
		
		self.boutons_manette = {k: -1 for k in button}
		self.axis_manette = {k: -1 for k in axis}
		self.dpad_manette = {k: -1 for k in dpad}
	
	def load(self):
		if self.name in self.sauvegarde.keys():
			self.boutons_manette = self.sauvegarde[self.name]["button"]
			self.axis_manette = self.sauvegarde[self.name]["axis"]
			self.dpad_manette = self.sauvegarde[self.name]["dpad"]
		else:
			self.default_button_axis_dpad()
	
	def save(self):
		self.sauvegarde[self.name] = {
			"button": self.boutons_manette,
			"axis": self.axis_manette,
			"dpad": self.dpad_manette
			}
		with open(self.fichier_sauvegarde, "wb") as sauvegarde:
			sauvegarde = Pickler(sauvegarde)
			sauvegarde.dump(self.sauvegarde)
	
	"""------------------------------------------------------------------"""
	
	@property
	def button_list(self):
		return self.__button_list
	
	@property
	def axis_list(self):
		return self.__axis_list
	
	@property
	def dpad_list(self):
		return self.__dpad_list
	
	"""------------------------------------------------------------------"""
	
	def value(self, event):
		return self.__getitem__(event, 0)
	
	def __getitem__(self, event, v=1):
		event = event.upper()
		self.__test(event)
		return self.__get_value(event, v)
	
	def __setitem__(self, event, id):
		event = event.upper()
		self.__test(event)
		self.__set_value(event, id)
	
	def __test(self, event):
		if event not in self.button_list + self.axis_list + self.dpad_list:
			raise pygame.error("{} n'est pas reconnu".format(event))
	
	def __get_value(self, event, v):
		if event in self.button_list:
			state = self.__get_button(event)
			value = self.boutons_manette[event] if event in self.boutons_manette.keys() else self.axis_manette[event]
		elif event in self.axis_list:
			state = self.__get_axis(event)
			value = self.axis_manette[event]
		elif event in self.dpad_list:
			arrow = self.dpad_manette[event]
			if type(arrow) is tuple:
				arrow = (arrow[2] if arrow[1] == 0 else 0, arrow[2] if arrow[1] == 1 else 0)
			state = self.__get_dpad(event)
			value = arrow
		
		return [value, state][v]
	
	def __set_value(self, event, id):
		try:
			id = tuple(id)
		except TypeError:
			pass
		try:
			if (event in ["A", "B", "X", "Y", "L1", "R1", "SELECT", "START", "L3", "R3", "AXIS_LEFT_X", "AXIS_LEFT_Y", "AXIS_RIGHT_X", "AXIS_RIGHT_Y"] and type(id) is not int) \
			or (event in ["L2", "R2"] and type(id) not in [int, tuple]) \
			or (event in ["UP", "DOWN", "LEFT", "RIGHT"] and type(id) not in [int, tuple]):
				raise ValueError
			if (event in ["L2", "R2"] and type(id) is tuple and len(id) != 2) \
			or (event in ["UP", "DOWN", "LEFT", "RIGHT"] and type(id) is tuple and len(id) != 3):
				raise ValueError
		except ValueError:
			raise pygame.error("Valeur {} non valide".format(id))
		else:
			if (event in ["A", "B", "X", "Y", "L1", "R1", "SELECT", "START", "L3", "R3"]) or (event in ["L2", "R2"] and type(id) is int):
				self.__set_button(event, id)
			elif (event in ["AXIS_LEFT_X", "AXIS_LEFT_Y", "AXIS_RIGHT_X", "AXIS_RIGHT_Y"]) or (event in ["L2", "R2"] and type(id) is tuple):
				self.__set_axis(event, id)
			elif event in ["UP", "DOWN", "LEFT", "RIGHT"]:
				self.__set_dpad(event, id)
			self.save()
	
	def __set_button(self, button, i):
		self.boutons_manette[button] = i
		try:
			del self.axis_manette[button]
		except KeyError:
			pass
	
	def __set_axis(self, axis, i):
		self.axis_manette[axis] = i
		try:
			del self.boutons_manette[axis]
		except KeyError:
			pass
	
	def __set_dpad(self, arrow, i):
		self.dpad_manette[arrow] = i
	
	def __get_button(self, id):
		try:
			id = self.boutons_manette[id]
			button = self.button_value[id]
		except (KeyError, TypeError):
			if type(id) is not tuple:
				id = self.axis_manette[id]
			axis, signe = id
			button = bool(self.axis_value[axis] > 0.1) if signe == "+" else bool(self.axis_value[axis] < -0.1)
		finally:
			return button
		
	def __get_axis(self, id):
		return self.axis_value[self.axis_manette[id]]
	
	def __get_dpad(self, id):
		arrow = self.dpad_manette[id]
		if type(arrow) is tuple:
			dpad = bool(self.hat_value[arrow[0]][arrow[1]] == arrow[2])
		elif type(arrow) is int:
			dpad = self.button_value[arrow]
		return dpad
	
	"""------------------------------------------------------------------"""
	
	@property
	def name(self):
		return self.__n
	
	@property
	def id(self):
		return self.__id_manette
	
	@id.setter
	def id(self, v):
		if v is not None:
			self.__id_manette = str(v)
		else:
			self.__id_manette = ""
	
	"""------------------------------------------------------------------"""
	
	A = property(lambda self: self.__get_value("A", 0), lambda self, id: self.__set_value("A", id))
	B = property(lambda self: self.__get_value("B", 0), lambda self, id: self.__set_value("B", id))
	X = property(lambda self: self.__get_value("X", 0), lambda self, id: self.__set_value("X", id))
	Y = property(lambda self: self.__get_value("Y", 0), lambda self, id: self.__set_value("Y", id))
	L1 = property(lambda self: self.__get_value("L1", 0), lambda self, id: self.__set_value("L1", id))
	L2 = property(lambda self: self.__get_value("L2", 0), lambda self, id: self.__set_value("L2", id))
	L3 = property(lambda self: self.__get_value("L3", 0), lambda self, id: self.__set_value("L3", id))
	R1 = property(lambda self: self.__get_value("R1", 0), lambda self, id: self.__set_value("R1", id))
	R2 = property(lambda self: self.__get_value("R2", 0), lambda self, id: self.__set_value("R2", id))
	R3 = property(lambda self: self.__get_value("R3", 0), lambda self, id: self.__set_value("R3", id))
	SELECT = property(lambda self: self.__get_value("SELECT", 0), lambda self, id: self.__set_value("SELECT", id))
	START = property(lambda self: self.__get_value("START", 0), lambda self, id: self.__set_value("START", id))
	UP = property(lambda self: self.__get_value("UP", 0), lambda self, id: self.__set_value("UP", id))
	DOWN = property(lambda self: self.__get_value("DOWN", 0), lambda self, id: self.__set_value("DOWN", id))
	LEFT = property(lambda self: self.__get_value("LEFT", 0), lambda self, id: self.__set_value("LEFT", id))
	RIGHT = property(lambda self: self.__get_value("RIGHT", 0), lambda self, id: self.__set_value("RIGHT", id))
	AXIS_LEFT_X = property(lambda self: self.__get_value("AXIS_LEFT_X", 0), lambda self, id: self.__set_value("AXIS_LEFT_X", id))
	AXIS_LEFT_Y = property(lambda self: self.__get_value("AXIS_LEFT_Y", 0), lambda self, id: self.__set_value("AXIS_LEFT_Y", id))
	AXIS_RIGHT_X = property(lambda self: self.__get_value("AXIS_RIGHT_X", 0), lambda self, id: self.__set_value("AXIS_RIGHT_X", id))
	AXIS_RIGHT_Y = property(lambda self: self.__get_value("AXIS_RIGHT_Y", 0), lambda self, id: self.__set_value("AXIS_RIGHT_Y", id))