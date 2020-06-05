# -*- coding: Utf-8 -*

from modules.init import *
from modules.classes import *

class Garage:
	
	def __init__(self, jeu):
		self.jeu = jeu
		
		#Images
		self.garage = images["garage"]
		self.piece = images["piece"]
		self.cadenas = images["cadenas"]
		
		#Polices d'écriture
		self.money_font = fonts("calibri", 70)
		self.stats_font = self.option_font = fonts("calibri", 40)
		self.valid_font = fonts("calibri", 60)
		self.choix_environnement_font = fonts("calibri", 80)
		
		#Objets Widget
		self.widget = Widget()
		
		#Environment
		self.environnements = {
			None: {"color":None, "img":None},
			"banlieue":{"color":SUB, "img":images["environnement"]["banlieue"]},
			"desert":{"color":SAND, "img":images["environnement"]["desert"]},
			"automne":{"color":AUTUMN, "img":images["environnement"]["automne"]},
			"neige":{"color":SNOW, "img":images["environnement"]["neige"]}
			}
		self.environnement_display = {}
		for i, nom in enumerate(["banlieue", "desert", "automne", "neige"], 1):
			image = self.environnements[nom]["img"]
			r_i = image.get_rect()
			if r_i.w > r_i.h:
				image = changer_taille_image(image, width=180)
			elif r_i.w < r_i.h:
				image = changer_taille_image(image, height=180)
			else:
				image = changer_taille_image(image, size=(180, 180))
			self.environnement_display[nom] = self.widget.Bouton(2, i, tag="environnement", type="img", img=image, shown_bg=True, bg=self.environnements[nom]["color"], outline=(2, BLACK))
		
		#Boutons
		self.boutons = {
			"fleche_bleue": self.widget.Bouton(1, 1, tag=("garage", "environnement"), type="img", sound="retour", img=images["fleche_bleue"]),
			"fleche_gauche": self.widget.Bouton(2, 1, tag="garage", type="img", sound="selection", img=images["fleche_garage_gauche"], validate_key=K_LEFT, validate_button="LEFT"),
			"fleche_droite": self.widget.Bouton(2, 1, tag="garage", type="img", sound="selection", img=images["fleche_garage_droite"], validate_key=K_RIGHT, validate_button="RIGHT"),
			"prix": self.widget.Bouton(3, 1, tag="garage", type="both", text="", font=("calibri", 35), img=changer_taille_image(self.piece, size=(35, 35))),
			"jouer": self.widget.Bouton(4, 1, tag="garage", text="JOUER", font=self.option_font),
			"croix_rouge": self.widget.Bouton(1, 1, tag="prix", type="img", sound="selection", img=images["croix_rouge"]),
			"validation": self.widget.Bouton(2, 1, tag="prix", text="", font=self.valid_font),
			}
	
	def run(self):
		#Voitures
		self.voiture_choisie = 0
		self.voiture = sauvegarde["voiture"]
		
		#Environment
		self.environnement = None
				
		#Sons
		sons.play("garage")
		
		option = 0
		self.widget.tag = "garage"
		self.widget.ligne = 2
		
		quitter_garage = False
		while not quitter_garage:
			
			self.afficher_garage(option)
			pygame.display.flip()
			
			event = pygame.event.poll()
			self.jeu.quitter = quitter_garage = fermer_fenetre()
			screenshot(event, fenetre)
			
			self.boutons["fleche_gauche"].state = bool(self.voiture > 1)
			self.boutons["fleche_droite"].state = bool(self.voiture < nbre_de_voitures_joueur)
			self.boutons["prix"].state = bool(not self.voiture_possédée)
			
			self.widget[event]
			
			if (event.type == KEYUP and event.key == K_ESCAPE) \
			or (event.type == JOYBUTTONUP and event.button == controller.B):
				self.boutons["fleche_bleue"].clicked = True
				
			#Fleche bleue
			if self.boutons["fleche_bleue"].clicked:
				if self.widget.tag == "garage":
					quitter_garage = True
				elif self.widget.tag == "environnement":
					option = 0
					self.widget.tag = "garage"
					self.widget.ligne = 2
			#Fleche gauche
			if self.boutons["fleche_gauche"].clicked:
				self.voiture -= 1
			#Fleche droite
			if self.boutons["fleche_droite"].clicked:
				self.voiture += 1
			#Prix
			if self.boutons["prix"].clicked:
				option = 1
				self.widget.tag = "prix"
			
			#Croix rouge
			if self.boutons["croix_rouge"].clicked:
				option = 0
				self.widget.tag = "garage"
				self.widget.ligne = 2
			
			#Validation achat
			if self.boutons["validation"].clicked:
				if infos_vehicules[self.voiture]["prix"] <= sauvegarde["argent"]:
					sauvegarde["argent"] -= infos_vehicules[self.voiture]["prix"]
					sauvegarde["voitures_possédées"][self.voiture] = True
				self.widget.tag = "garage"
			#Jouer
			if sauvegarde["voitures_possédées"][self.voiture] and self.boutons["jouer"].clicked:
				option = 2
				self.widget.tag = "environnement"
				self.widget.ligne = 2
				self.widget.colonne = 1
			#Environment
			for nom, env in self.environnement_display.items():
				if env.clicked:
					self.environnement = nom
					break
			if self.environnement is not None:
				self.voiture_choisie = self.voiture
				quitter_garage = True
		
		if sauvegarde["voitures_possédées"][self.voiture]:
			sauvegarde["voiture"] = self.voiture
		
		return self.voiture_choisie, self.environnements[self.environnement]
	
	def afficher_garage(self, option=0):
		clock.tick(60)
		
		fenetre.fill(GRAY)
		self.boutons["fleche_bleue"].afficher(x=ecran.left+5, y=ecran.top+5)
		
		#Argent
		piece = afficher_image(fenetre, self.piece, height=50, right=ecran.right-5, top=ecran.top+5)
		afficher_texte(fenetre, sauvegarde["argent"], self.money_font, color=YELLOW, top=ecran.top+5, right=piece.left-5)
		
		#Meilleur score
		m_s = afficher_texte(fenetre, "Meilleur score:", self.money_font, color=YELLOW, bottom=ecran.bottom-5, left=ecran.left+5)
		afficher_texte(fenetre, sauvegarde["meilleur_score"], self.money_font, color=YELLOW, bottom=ecran.bottom-5, left=m_s.right+10)
		
		if option < 2:
			voiture = afficher_image(fenetre, self.garage[self.voiture], center=ecran.center)
			
			#Fleche gauche
			if self.voiture > 1:
				self.boutons["fleche_gauche"].afficher(left=ecran.left+50, centery=ecran.centery)
			#Fleche droite
			if self.voiture < nbre_de_voitures_joueur:
				self.boutons["fleche_droite"].afficher(right=ecran.right-50, centery=ecran.centery)
			
			#Récupération des informations des véhicules
			vitesses = []
			accélérations = []
			maniabilités = []
			freinages = []
			for i in range(nbre_de_voitures_joueur):
				vitesses.append(infos_vehicules[i+1]["vitesse_max"])
				accélérations.append(infos_vehicules[i+1]["accélération"])
				maniabilités.append(infos_vehicules[i+1]["maniabilité"])
				freinages.append(infos_vehicules[i+1]["freinage"])
			
			max_v = max(vitesses) * 1.10
			max_a = min(accélérations) * 0.90
			max_m = max(maniabilités) * 1.30
			max_f = min(freinages) * 0.80
			
			# - Taille cadre
			size = (300, 30)
			
			#Vitesse/Acceleration
			v = infos_vehicules[self.voiture]["vitesse_max"]
			a = infos_vehicules[self.voiture]["accélération"]
			vitesse_acceleration = (v + max_a)/(max_v + a)
			c = dessiner_barre_stats(fenetre, size, vitesse_acceleration, color=GREEN, outline=3, bottom=voiture.top-150, centerx=voiture.centerx+100)
			afficher_texte(fenetre, "Vitesse/Acc.", self.stats_font, right=c.left-4, centery=c.centery)
			
			#Maniabilté
			m = infos_vehicules[self.voiture]["maniabilité"]
			maniabilité = m / max_m
			c = dessiner_barre_stats(fenetre, size, maniabilité, color=GREEN, outline=3, y=c.bottom+10, centerx=voiture.centerx+100)
			afficher_texte(fenetre, "Maniabilité", self.stats_font, right=c.left-4, centery=c.centery)
			
			#Freinage
			f = infos_vehicules[self.voiture]["freinage"]
			freinage = max_f / f
			c = dessiner_barre_stats(fenetre, size, freinage, color=GREEN, outline=3, y=c.bottom+10, centerx=voiture.centerx+100)
			afficher_texte(fenetre, "Freinage", self.stats_font, right=c.left-4, centery=c.centery)
			
			#Utilisable ou non
			self.voiture_possédée = sauvegarde["voitures_possédées"][self.voiture]
			self.boutons["jouer"].bg = (LIGHT_GREEN, DARK_GREEN) if self.voiture_possédée else (LIGHT_GRAY, DARK_GRAY)
			self.boutons["jouer"].sound = "validation" if self.voiture_possédée else "bloqué"
			self.boutons["jouer"].afficher(right=ecran.right-10, bottom=ecran.bottom-10)
			if not self.voiture_possédée:
				afficher_image(fenetre, self.cadenas, center=voiture.center)
				argent_en_possession = sauvegarde["argent"]
				prix_du_vehicule = infos_vehicules[self.voiture]["prix"]
				self.boutons["prix"].text = prix_du_vehicule
				self.boutons["prix"].afficher(centerx=ecran.centerx, top=voiture.bottom+25) #ecran.centery+77
			
			if option == 1:
				
				#Assombrir l'écran
				voile_transparent(fenetre, BLACK, 170)
				
				#Cadre d'achat
				w = 0.5*ecran.width
				h = 0.5*ecran.height
				cadre = dessiner_rectangle(fenetre, GREEN, center=ecran.center, w=w, h=h, outline=3)
				#Croix rouge
				self.boutons["croix_rouge"].afficher(top=cadre.top+5, left=cadre.left+5)
				
				if prix_du_vehicule <= argent_en_possession:
					a = afficher_texte(fenetre, "Etes-vous sûr de vouloir", self.valid_font, centerx=cadre.centerx, y=cadre.y+100)
					b = afficher_texte(fenetre, "acheter ce véhicule?", self.valid_font, centerx=cadre.centerx, y=a.bottom)
					self.boutons["validation"].text = "OUI"
				else:
					a = afficher_texte(fenetre, "Vous ne pouvez pas encore", self.valid_font, centerx=cadre.centerx, y=cadre.y+100)
					b = afficher_texte(fenetre, "acheter ce véhicule", self.valid_font, centerx=cadre.centerx, y=a.bottom)
					self.boutons["validation"].text = "OK"
				self.boutons["validation"].afficher(centerx=cadre.centerx, bottom=cadre.bottom-10)
		else:
			w, h = size = (200, 200)
			l = len(self.environnement_display)
			e = ecart = 15
			
			r = generer_rect(width=w*l+e*(l-1), height=h, center=ecran.center)
			x = r.x
			
			for nom, env in self.environnement_display.items():
				r = env.afficher(x=x, centery=ecran.centery, size=size)
				x = r.right + ecart
				afficher_texte(fenetre, nom.upper(), fonts("calibri", 50), color=DARK_GREEN, centerx=r.centerx, top=r.bottom+5)
			
			afficher_texte(fenetre, "ENVIRONNEMENT", fonts("calibri", 90), color=GREEN, centerx=ecran.centerx, bottom=r.top-10)
		#FPS
		clock.afficher(fenetre, centerx=ecran.centerx, top=ecran.top+10)