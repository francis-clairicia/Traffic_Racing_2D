#-*- coding:Utf-8 -*

import sys
import os
import pygame
from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.key.set_repeat(25, 100)

""" Fonctions/classes permettant une utilisation plus facile de PYGAME """
########## CLASSES ##########

class FPS:
	def __init__(self, show=False):
		self.clock = pygame.time.Clock()
		self.color = (0, 0, 255)
		self.font = fonts("calibri", 45)
		self.show = show
	
	@property
	def font(self):
		return self.__font
	
	@font.setter
	def font(self, font):
		if isinstance(font, (tuple, list)):
			self.__font = fonts(*font)
		elif isinstance(font, pygame.font.Font):
			self.__font = font
	
	@property
	def show(self):
		return self.__show
	
	@show.setter
	def show(self, v):
		self.__show = bool(v)
	
	def tick(self, framerate=0):
		self.clock.tick_busy_loop(framerate)
	
	def get_fps(self):
		return self.clock.get_fps()
	
	def afficher(self, surface, **kwargs):
		if self.show:
			fps = round(self.clock.get_fps(), 2)
			size = sum([rect_text(t, self.font, "width") for t in (fps, "FPS")]), max([rect_text(t, self.font, "height") for t in (fps, "FPS")])
			rect = generer_rect(size=size, **kwargs)
			afficher_texte(surface, fps, self.font, color=self.color, centery=rect.centery, left=rect.left)
			afficher_texte(surface, "FPS", self.font, color=self.color, centery=rect.centery, right=rect.right)
			return rect
		else:
			return None

class Clavier:
	
	def __init__(self, clavier="QWERTY"):
		
		self.touches = { # Ceci est la liste des touches
			K_0:           "0",
			K_1:           "1",
			K_2:           "2",
			K_3:           "3",
			K_4:           "4",
			K_5:           "5",
			K_6:           "6",
			K_7:           "7",
			K_8:           "8",
			K_9:           "9",
			K_a:           "A",
			K_b:           "B",
			K_c:           "C",
			K_d:           "D",
			K_e:           "E",
			K_f:           "F",
			K_g:           "G",
			K_h:           "H",
			K_i:           "I",
			K_j:           "J",
			K_k:           "K",
			K_l:           "L",
			K_m:           "M",
			K_n:           "N",
			K_o:           "O",
			K_p:           "P",
			K_q:           "Q",
			K_r:           "R",
			K_s:           "S",
			K_t:           "T",
			K_u:           "U",
			K_v:           "V",
			K_w:           "W",
			K_x:           "X",
			K_y:           "Y",
			K_z:           "Z",
			K_KP0:         "KP 0",
			K_KP1:         "KP 1",
			K_KP2:         "KP 2",
			K_KP3:         "KP 3",
			K_KP4:         "KP 4",
			K_KP5:         "KP 5",
			K_KP6:         "KP 6",
			K_KP7:         "KP 7",
			K_KP8:         "KP 8",
			K_KP9:         "KP 9",
			K_UP:          "UP",
			K_DOWN:        "DOWN",
			K_RIGHT:       "RIGHT",
			K_LEFT:        "LEFT",
			}
		
		self.set(clavier)
	
	def __contains__(self, touche):
		return bool(touche in self.touches.keys())
	
	def __getitem__(self, touche):
		if isinstance(touche, int):
			return self.touches.get(touche)
		elif isinstance(touche, str):
			v = None
			for key, value in self.touches.items():
				if value == touche.upper():
					v = key
					break
			return v
		else:
			return None
	
	def set(self, clavier):
		self.type = clavier = clavier.upper()
		if clavier not in ["AZERTY", "QWERTY", "QWERTZ"]:
			raise pygame.error(clavier + " is not QWERTY or AZERTY or QWERTZ")
		
		touches = (
			97, #A
			113, #Q
			119, #W
			121, #Y
			122, #Z
			)

		if clavier == "AZERTY":
			K_q, K_a, K_z, K_y, K_w = touches
		elif clavier == "QWERTY":
			K_a, K_q, K_w, K_y, K_z = touches
		elif clavier == "QWERTZ":
			K_a, K_q, K_w, K_z, K_y = touches
		
		self.touches[K_a] = "A"
		self.touches[K_q] = "Q"
		self.touches[K_w] = "W"
		self.touches[K_y] = "Y"
		self.touches[K_z] = "Z"

######### FONCTIONS #########

def find_value(value, iterable):
	def search(value, iterable):
		if iterable == value:
			yield iterable
		elif isinstance(iterable, dict):
			for k, v in iterable.items():
				for result in search(value, v):
					yield result
		elif isinstance(iterable, (tuple, list)):
			for v in iterable:
				for result in search(value, v):
					yield result
	return list(search(value, iterable))

def path(*args):
	f = os.path.join(*args)
	if not f.startswith(tuple([disk + ":\\" for disk in ["C", "D", "E", "F"]])):
		f = os.path.join(sys.path[0], *args)
	return f

def fonts(*args, **kwargs):
	if len(args) == 2:
		font = pygame.font.SysFont(*args, **kwargs)
	else:
		font = pygame.font.SysFont(pygame.font.get_default_font(), args[1], **kwargs)
	return font

def fermer_fenetre():
	keys = pygame.key.get_pressed()
	if keys[K_LALT] and keys[K_F4]:
		return True
	else:
		return False

def screenshot(event, surface):
	if event.type == KEYUP and event.key == K_F11:
		i = 1
		while os.path.isfile(f"screenshot_{i}.jpg"):
			i += 1
		pygame.image.save(surface, f"screenshot_{i}.jpg")

def voile_transparent(surface, couleur, niveau_de_transparence, rect=None, **kwargs):
	#Assombrir l'écran
	if rect is None:
		size = surface.get_size()
		rect = generer_rect(size=size, **kwargs)
	else:
		size = rect.size
	s = pygame.Surface(size, pygame.SRCALPHA)   # per-pixel alpha
	assert niveau_de_transparence in range(256)
	voile = list(couleur) + [niveau_de_transparence]
	s.fill(voile)
	surface.blit(s, rect)

########### Images ###########
def charger_image(image, **kwargs):
	image = pygame.image.load(image).convert_alpha()
	if len(kwargs) > 0: #S'il y a des modifications pour l'image
		image = changer_taille_image(image, **kwargs)
	return image

def changer_taille_image(image, size=None, width=0, height=0):
	if size is not None:
		image = pygame.transform.smoothscale(image, size)
	
	elif width > 0 and height > 0:
		image = pygame.transform.smoothscale(image, (width, height))
	else:
		w, h = image.get_size()
		if width > 0:
			image = pygame.transform.rotozoom(image, 0, width/w)
		elif height > 0:
			image = pygame.transform.rotozoom(image, 0, height/h)
	return image

########### Surfaces ###########
def afficher_image(surface, image, rect=None, size=None, width=0, height=0, **kwargs):
	image = changer_taille_image(image, size, width, height)
	rect = generer_rect(rect, image, **kwargs)
	surface.blit(image, rect)
	return rect

def afficher_texte(surface, texte, font, rect=None, color=(0, 0, 0), shadow=False, shadow_pos=(3, 3) , shadow_color=(0, 0, 0), **kwargs):
	try:
		font = fonts(*font)
	except TypeError:
		pass
	
	if texte is not None:
		t = type(texte)
		texte = str(texte)
		if t in [int, float]:
			if t is float:
				dot = texte.find(".")
				texte_after_dot = texte[dot+1:]
				texte_int = texte[:dot]
			else:
				texte_int = texte
			texte = ""
			k = 0
			for i in range(len(texte_int), 0, -1):
				k += 1
				if (k % 3 == 1) and (k != 1):
					texte = " " + texte
				texte = texte_int[i-1] + texte
			if t is float:
				texte += "." + texte_after_dot
	else:
		texte = ""
	rendu = font.render(texte, 1, color)
	
	rect = generer_rect(rect, rendu, **kwargs)
	
	if shadow:
		rendu2 = font.render(texte, 1, shadow_color)
		surface.blit(rendu2, (rect.x+shadow_pos[0], rect.y+shadow_pos[1]))
	surface.blit(rendu, rect)
	
	return rect

def dessiner_rectangle(surface, color, rect=None, outline=0, outline_color=(0, 0, 0), **kwargs):
	rect = generer_rect(rect, **kwargs)
	if color:
		pygame.draw.rect(surface, color, rect)
	if outline > 0:
		pygame.draw.rect(surface, outline_color, rect, outline)
	return rect

def dessiner_barre_stats(surface, size, pourcentage, color=(0, 0, 0), outline=2, outline_color=(0, 0, 0), **kwargs):
	width, height = size
	cadre = generer_rect(size=size, **kwargs)
	barre = modifier_rect(cadre, w=width*pourcentage)
	dessiner_rectangle(surface, color, barre)
	dessiner_rectangle(surface, None, cadre, outline=outline, outline_color=outline_color)
	return cadre

def dessiner_cercle(surface, color, centre, rayon, outline=0, outline_color=(0, 0, 0)):
	if color:
		rect = pygame.draw.circle(surface, color, centre, rayon)
	if outline > 0:
		rect = pygame.draw.circle(surface, outline_color, centre, rayon, outline)
	return rect

########## Rect ###########
def generer_rect(rect=None, surface=None, **kwargs):
	if surface is not None:
		if rect is None:
			rect = surface.get_rect(**kwargs)
		elif type(rect) in [tuple, list]:
			if len(rect) == 2:
				rect = surface.get_rect(topleft=rect, **kwargs)
			elif len(rect) == 4:
				rect = modifier_rect(rect, **kwargs)
		elif len(kwargs) > 0:
			rect = modifier_rect(rect, **kwargs)
	else:
		if rect is None:
			rect = pygame.Rect(0, 0, 0, 0)
		if (type(rect) in [tuple, list]) or (len(kwargs) > 0):
			rect = modifier_rect(rect, **kwargs)
	return rect

def rect_text(texte, font, value=None):
	texte = str(texte) if texte is not None else ""
	rect = font.render(texte, 1, (0, 0, 0)).get_rect()
	return rect_value(rect, value) if value is not None else rect

def modifier_rect(rect, **kwargs):
	if type(rect) in [tuple, list]:
		rect = pygame.Rect(*rect)
	else:
		rect = rect.copy()
	
	# Taille du rectangle
	if "size" in kwargs.keys():
		rect.size = kwargs["size"]
	if "width" in kwargs.keys():
		rect.w = kwargs["width"]
	if "height" in kwargs.keys():
		rect.h = kwargs["height"]
	if "w" in kwargs.keys():
		rect.w = kwargs["w"]
	if "h" in kwargs.keys():
		rect.h = kwargs["h"]
	
	#Position du rectangle
	if "x" in kwargs.keys():
		rect.x = kwargs["x"]
	if "y" in kwargs.keys():
		rect.y = kwargs["y"]
	if "top" in kwargs.keys():
		rect.top = kwargs["top"]
	if "left" in kwargs.keys():
		rect.left = kwargs["left"]
	if "bottom" in kwargs.keys():
		rect.bottom = kwargs["bottom"]
	if "right" in kwargs.keys():
		rect.right = kwargs["right"]
	if "topleft" in kwargs.keys():
		rect.topleft = kwargs["topleft"]
	if "bottomleft" in kwargs.keys():
		rect.bottomleft = kwargs["bottomleft"]
	if "topright" in kwargs.keys():
		rect.topright = kwargs["topright"]
	if "bottomright" in kwargs.keys():
		rect.bottomright = kwargs["bottomright"]
	if "midtop" in kwargs.keys():
		rect.midtop = kwargs["midtop"]
	if "midleft" in kwargs.keys():
		rect.midleft = kwargs["midleft"]
	if "midbottom" in kwargs.keys():
		rect.midbottom = kwargs["midbottom"]
	if "midright" in kwargs.keys():
		rect.midright = kwargs["midright"]
	if "center" in kwargs.keys():
		rect.center = kwargs["center"]
	if "centerx" in kwargs.keys():
		rect.centerx = kwargs["centerx"]
	if "centery" in kwargs.keys():
		rect.centery = kwargs["centery"]
	
	return rect

def rect_value(rect, value):
	if isinstance(rect, pygame.Surface):
		rect = rect.get_rect()
	
	# Taille du rectangle
	if value == "size":
		return rect.size
	elif (value == "width") or (value == "w"):
		return rect.width
	elif (value == "height") or (value == "h"):
		return rect.height
	
	#Position du rectangle
	elif value == "x":
		return rect.x
	elif value == "y":
		return rect.y
	elif value == "top":
		return rect.top
	elif value == "left":
		return rect.left
	elif value == "bottom":
		return rect.bottom
	elif value == "right":
		return rect.right
	elif value == "topleft":
		return rect.topleft
	elif value == "bottomleft":
		return rect.bottomleft
	elif value == "topright":
		return rect.topright
	elif value == "bottomright":
		return rect.bottomright
	elif value == "midtop":
		return rect.midtop
	elif value == "midleft":
		return rect.midleft
	elif value == "midbottom":
		return rect.midbottom
	elif value == "midright":
		return rect.midright
	elif value == "center":
		return rect.center
	elif value == "centerx":
		return rect.centerx
	elif value == "centery":
		return rect.centery
	else:
		return None