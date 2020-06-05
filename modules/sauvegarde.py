# -*- coding: Utf-8 -*

import sys
import os
from pickle import Pickler, Unpickler

class Sauvegarde:
	
	def __init__(self):
		
		self.default_save = {
			"meilleur_score": 0,
			"argent": 0,
			"voitures_possédées": {
				1:True,
				2:False,
				3:False,
				4:False,
				5:False,
				6:False,
				7:False,
				8:False,
				9:False
				},
			"voiture": 1,
			"fps": False,
			"musique": {
				"etat": True,
				"volume": 0.5
				},
			"sfx": {
				"etat": True,
				"volume": 0.5
				},
			"accélération_auto": False,
			"controles": {
				"accélérer": "RIGHT",
				"freiner": "LEFT",
				"haut": "UP",
				"bas": "DOWN"
				}
			}
		
		self.fichier_sauvegarde = os.path.join(sys.path[0], "files", "save.bin")
		if os.path.isfile(self.fichier_sauvegarde):
			with open(self.fichier_sauvegarde, "rb") as sauvegarde:
				sauvegarde = Unpickler(sauvegarde)
				self.sauvegarde = sauvegarde.load()
		else:
			self.reset()
	
	def __getitem__(self, clé):
		return self.sauvegarde[clé]
	
	def __setitem__(self, clé, valeur):
		self.sauvegarde[clé] = valeur
	
	def dump(self):
		with open(self.fichier_sauvegarde, "wb") as sauvegarde:
			sauvegarde = Pickler(sauvegarde)
			sauvegarde.dump(self.sauvegarde)
	def reset(self):
		self.sauvegarde = dict(self.default_save)