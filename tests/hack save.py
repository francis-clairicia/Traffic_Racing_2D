# -*- coding:utf-8 -*

import sys
import os
import pickle

print("-----------------------Hack sauvegarde Traffic Racing 2D------------------------")
print("Création en cours...")

fichier_sauvegarde = os.path.join(os.path.dirname(sys.path[0]), "files", "save.bin")
if os.path.isfile(fichier_sauvegarde):
	with open(fichier_sauvegarde, "rb") as sauvegarde:
		save = dict(pickle.load(sauvegarde))
	save["money"] = pow(10, 9) - 1
	save["owned_cars"] = {i + 1: True for i in range(9)}
	with open(fichier_sauvegarde, "wb") as sauvegarde:
		pickle.dump(save, sauvegarde)
print("Terminé")
print("----------------------------------------------------")
os.system("pause")