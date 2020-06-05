# -*- coding:utf-8 -*

import sys
import os
import pygame
from pygame.locals import *
from pickle import Pickler

print("-----------------------Hack sauvegarde Traffic Racing 2D------------------------")
print("Création en cours...")
hack_save = {
	"meilleur_score": 0,
	"argent": 50000,
	"voitures_possédées": {
		1:True,
		2:True,
		3:True,
		4:True,
		5:True,
		6:True,
		7:True,
		8:True,
		9:True
		},
	"voiture": 1,
	"options": {
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
			"accélérer": K_RIGHT,
			"freiner": K_LEFT,
			"haut": K_UP,
			"bas": K_DOWN
			}
		}
	}

fichier_sauvegarde = os.path.join(os.path.dirname(sys.path[0]), "files", "save.bin")
with open(fichier_sauvegarde, "wb") as sauvegarde:
	sauvegarde = Pickler(sauvegarde)
	sauvegarde.dump(hack_save)
print("Terminé")
print("----------------------------------------------------")
os.system("pause")