# -*- coding: Utf-8 -*

from my_pygame import set_constant_directory, set_constant_file

# Colors
SUB = (140, 255, 140)
SAND = (223, 232, 49)
SNOW = (224, 224, 224)
AUTUMN = (194, 255, 38)

#Dossiers
IMG_FOLDER = set_constant_directory("files", "img")
AUDIO_FOLDER = set_constant_directory("files", "sounds")
FONT_FOLDER = set_constant_directory("files", "fonts")

#Icone
ICON = set_constant_file(IMG_FOLDER, "icone.ico")

IMG = {
    ########## Logo/Image de fond du jeu ##########
    "logo": set_constant_file(IMG_FOLDER, "logo.png"),
    "background": set_constant_file(IMG_FOLDER, "wallpaper.jpg"),
    ########## Items ##########
    "red_cross": set_constant_file(IMG_FOLDER, "croix_rouge.png"),
    "red_cross_hover": set_constant_file(IMG_FOLDER, "croix_rouge_over.png"),
    "blue_arrow": set_constant_file(IMG_FOLDER, "blue_arrow.png"),
    "green_arrow": set_constant_file(IMG_FOLDER, "green_arrow.png"),
    "green_valid": set_constant_file(IMG_FOLDER, "valide.png"),
    "left_arrow": set_constant_file(IMG_FOLDER, "fleche_garage_gauche.png"),
    "left_arrow_hover": set_constant_file(IMG_FOLDER, "fleche_garage_gauche_over.png"),
    "right_arrow": set_constant_file(IMG_FOLDER, "fleche_garage_droite.png"),
    "right_arrow_hover": set_constant_file(IMG_FOLDER, "fleche_garage_droite_over.png"),
    "piece": set_constant_file(IMG_FOLDER, "piece.png"),
    "cadenas": set_constant_file(IMG_FOLDER, "cadenas.png"),
    "explosion": set_constant_file(IMG_FOLDER, "explosion.png"),
    "new_high_score": set_constant_file(IMG_FOLDER, "high_score.png")
}

FONT = {
    "algerian": set_constant_file(FONT_FOLDER, "Algerian Regular.ttf")
}

########## Musiques/Sons ##########
AUDIO = {
    # Musiques
    "menu": set_constant_file(AUDIO_FOLDER, "menu.wav"),
    "garage": set_constant_file(AUDIO_FOLDER, "garage.wav"),
    "gameplay": set_constant_file(AUDIO_FOLDER, "gameplay.wav"),
    # SFX
    "back": set_constant_file(AUDIO_FOLDER, "sfx-menu-back.wav"),
    "select": set_constant_file(AUDIO_FOLDER, "sfx-menu-select.wav"),
    "validate": set_constant_file(AUDIO_FOLDER, "sfx-menu-validate.wav"),
    "block": set_constant_file(AUDIO_FOLDER, "sfx-menu-block.wav"),
    "crash": set_constant_file(AUDIO_FOLDER, "sfx-crash.wav")
}

########## Image des voitures ##########
#--- Voitures utilisables
IMG["garage_cars"] = dict()
IMG["gameplay_cars"] = dict()
nb_player_cars = 9
for i in range(nb_player_cars):
    i += 1
    IMG["garage_cars"][i] = set_constant_file(IMG_FOLDER, "garage", f"voiture_{i}.png")
    IMG["gameplay_cars"][i] = list()
    for n in range(10):
        try:
            image = set_constant_file(IMG_FOLDER, "gameplay", f"voiture_{i}", f"{n+1}.png")
        except FileNotFoundError:
            continue
        else:
            IMG["gameplay_cars"][i].append(image)
#--- Voitures obstacles
IMG["traffic"] = {"normal":{}, "opposé":{}}
nb_traffic_car = 4
for i in range(nb_traffic_car):
    i += 1
    for sens in ("normal", "opposé"):
        IMG["traffic"][sens][i] = (
            set_constant_file(IMG_FOLDER, "gameplay", "traffic", f"cars_{i}_{sens}.png"),
            set_constant_file(IMG_FOLDER, "gameplay", "traffic", f"cars_{i}_{sens}-2.png")
        )

########## Image environnement ##########
IMG["environnement"] = {
    "banlieue": set_constant_file(IMG_FOLDER, "arbre.png"),
    "desert": set_constant_file(IMG_FOLDER, "cactus.png"),
    "automne": set_constant_file(IMG_FOLDER, "arbre_automne.png"),
    "neige": set_constant_file(IMG_FOLDER, "sapin.png")
}

########## Infos sur les véhicules ##########
# - prix en $
# - max_speed en km/h
# - acceleration en sec (le temps qu'il faut pour passer de 0 à 100km)
# - maniability en px/s
# - break en sec (le temps qu'il faut pour passer de max_speed à 0km)
CAR_INFOS = {
    1: {"prix": None, "max_speed": 80, "acceleration": 5, "maniability": 60, "break": 4},
    2: {"prix": 5000, "max_speed": 100, "acceleration": 4.6, "maniability": 72, "break": 3.5},
    3: {"prix": 12500, "max_speed": 120, "acceleration": 4.2, "maniability": 84, "break": 3.1},
    4: {"prix": 30000, "max_speed": 150, "acceleration": 3.5, "maniability": 90, "break": 2.8},
    5: {"prix": 55000, "max_speed": 180, "acceleration": 3.1, "maniability": 102, "break": 2.5},
    6: {"prix": 85000, "max_speed": 200, "acceleration": 2.8, "maniability": 120, "break": 2.3},
    7: {"prix": 100000, "max_speed": 230, "acceleration": 2.5, "maniability": 150, "break": 2},
    8: {"prix": 500000, "max_speed": 260, "acceleration": 2.3, "maniability": 162, "break": 1.7},
    9: {"prix": 1000000, "max_speed": 280, "acceleration": 2, "maniability": 180, "break": 1.5}
}