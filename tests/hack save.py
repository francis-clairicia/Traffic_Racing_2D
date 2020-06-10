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
    for car_id in save["owned_cars"]:
        save["owned_cars"][car_id] = True
    with open(fichier_sauvegarde, "wb") as sauvegarde:
        pickle.dump(save, sauvegarde)
print("Terminé")
print("----------------------------------------------------")
if sys.platform.startswith("win"):
    os.system("pause")