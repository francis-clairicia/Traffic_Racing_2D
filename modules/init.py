# -*- coding:Utf-8 -*

from donnees import *
from modules.sons import *
from modules.sauvegarde import *
from modules.chargement import *
from modules.controller import *

######### Chargement des fichiers #######
# images, sounds = Chargement(fichiers_images, fichiers_sons).start()

######### Initialisation des modules #########
sauvegarde = Sauvegarde()
# sons = Sons(sounds, sauvegarde)
# controller = Controller()
clavier = Clavier("azerty") #On définit le modèle de clavier utilisé