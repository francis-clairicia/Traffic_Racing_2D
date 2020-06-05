# -*- coding: Utf-8 -*

import pygame

class Sons:
	
	def __init__(self, sounds, sauvegarde):
		self.sauvegarde = sauvegarde
		#SFX
		self.sounds = {
			#Général
			"retour": sounds["retour"],
			"selection": sounds["selection"],
			"validation": sounds["validation"],
			"bloqué": sounds["bloqué"],
			#Gameplay
			"crash": sounds["crash"],
			}
		self.volume_sfx(sauvegarde["sfx"]["volume"])
		
		#BG Musics
		self.bg_musics = {
			"menu": sounds["menu"],
			"garage": sounds["garage"],
			"gameplay": sounds["gameplay"]
			}
		self.volume_music(sauvegarde["musique"]["volume"])
	
	def __contains__(self, type):
		return bool(type in list(self.sounds.keys()) + list(self.bg_musics.keys()))
	
	def play(self, type, *args):
		if type in self:
			if type in self.sounds:
				self.play_sfx(type, *args)
			else:
				self.background_music(type)
		else:
			raise pygame.error("'" + type + "' n'est pas reconnu")
	
	def play_sfx(self, type, *args):
		if self.sauvegarde["sfx"]["etat"] is True:
			self.sounds[type].play(*args)
	
	def volume_sfx(self, volume):
		for sfx in self.sounds.values():
			sfx.set_volume(volume)
	
	def background_music(self, section):
		for musique in self.bg_musics.values():
			musique.stop()
		if self.sauvegarde["musique"]["etat"] is True:
			self.bg_musics[section].play(-1)
	
	def volume_music(self, volume):
		for musique in self.bg_musics.values():
			musique.set_volume(volume)