# -*- coding:Utf-8 -*

from donnees import *
from threading import Thread

class Chargement:
	
	def __init__(self, fichiers_images, fichiers_sons):
		self.fichiers_images = fichiers_images
		self.fichiers_sons = fichiers_sons
		self.fichiers_chargés = 0
		self.nbre_de_fichiers = 0
		self.images_chargées = {}
		self.sons_chargés = {}
	
	def start(self):
		
		def charger():
			
			# Compter le nombre de fichiers total avant de débuter
			for dossier, sous_dossiers, fichiers in os.walk(path("files")):
				for fichier in fichiers:
					fichier = path(dossier, fichier)
					if fichier.endswith((".png", ".jpg")):
						fichier_dans_la_liste = find_value(fichier, self.fichiers_images)
					elif fichier.endswith(".wav"):
						fichier_dans_la_liste = find_value(fichier, self.fichiers_sons)
					else:
						fichier_dans_la_liste = False
					self.nbre_de_fichiers += 1 if fichier_dans_la_liste else 0
			
			# Chargement des fichiers
			parametres = {nom: {} for nom in self.fichiers_images.keys()}
			parametres["logo"] = {"height": 200}
			parametres["background"] = {"width": ecran.width}
			parametres["fleche_verte"] = {"height": 40}
			parametres["explosion"] = {"size": (90,90)}
			parametres["nouveau_meilleur_score"] = {"width": 150}
			parametres["garage"] = {"height": 150}
			parametres["voitures_joueur"] = parametres["voitures_traffic"] = {"height": 55}
			
			for nom, element in self.fichiers_images.items():
				if type(element) is tuple:
					n = len(element)
					self.images_chargées[nom] = tuple(charger_image(element[i], **parametres[nom]) for i in range(n))
					self.fichiers_chargés += n
				elif type(element) is dict:
					self.images_chargées[nom] = {}
					if nom in ["garage", "environnement"]:
						for n, e in element.items():
							self.images_chargées[nom][n] = charger_image(e, **parametres[nom])
							self.fichiers_chargés += 1
					elif nom == "voitures_joueur":
						for n, e in element.items():
							self.images_chargées[nom][n] = []
							for img in e:
								self.images_chargées[nom][n].append(charger_image(img, **parametres[nom]))
								self.fichiers_chargés += 1
					elif nom == "voitures_traffic":
						for s, e in element.items():
							self.images_chargées[nom][s] = {}
							for a, img in e.items():
								n = len(img)
								self.images_chargées[nom][s][a] = tuple(charger_image(img[i], **parametres[nom]) for i in range(n))
								self.fichiers_chargés += n
				else:
					self.images_chargées[nom] = charger_image(element, **parametres[nom])
					self.fichiers_chargés += 1
			
			for nom, element in self.fichiers_sons.items():
				self.sons_chargés[nom] = pygame.mixer.Sound(element)
				self.fichiers_chargés += 1
		
		Thread(target=charger).start()
		while True:
			clock.tick(60)
			try:
				p = self.fichiers_chargés / self.nbre_de_fichiers
			except ZeroDivisionError:
				p = 0
			finally:
				w = 250
				h = 40
				
				t = afficher_texte(fenetre, "CHARGEMENT", ("calibri", 55), color=WHITE, bottom=ecran.centery-5, centerx=ecran.centerx)
				d = dessiner_barre_stats(fenetre, (t.w, h), p, color=GREEN, outline=3, outline_color=YELLOW, top=ecran.centery+5, centerx=ecran.centerx)
				
				pygame.display.update([t, d])
				pygame.event.pump()
				if p == 1:
					break
		print([self.fichiers_chargés, self.nbre_de_fichiers])
		
		return self.images_chargées, self.sons_chargés