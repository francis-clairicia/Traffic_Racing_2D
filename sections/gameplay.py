# -*- coding: Utf-8 -*

from modules.init import *
from modules.classes import *

class Gameplay:
	
	def __init__(self, jeu):
		self.jeu = jeu
		
		#Police d'écriture
		font = "cooperblack"
		self.gameplay_font = fonts(font, 45)
		self.gameplay_font_2 = fonts(font, 90)
		
		#Autres images
		self.fleche_verte = images["fleche_verte"]
		self.image_explosion = images["explosion"]
		self.image_nouveau_meilleur_score = images["nouveau_meilleur_score"]
		self.piece = images["piece"]
		
	def run(self, voiture, environnement, options):
				
		#Environnement
		self.couleur_de_fond = environnement["color"]
		self.image_background = changer_taille_image(environnement["img"], height=110)
		
		self.quitter_partie = False
		while not self.quitter_partie:
		
			#Initialisation du jeu
			self.init_gameplay(voiture)
			
			#Sons
			sons.play("gameplay")
			
			while not self.partie_finie:
				#Afficher le jeu
				self.afficher_jeu()
				
				if self.chrono < self.compte_a_rebours:
					afficher_texte(fenetre, int(self.compte_a_rebours - self.chrono + 1), self.gameplay_font_2, color=YELLOW, shadow=True, center=ecran.center)
				
				pygame.display.flip()
				
				if self.chrono >= self.compte_a_rebours:
					#Recevoir les commandes
					ACCELERATION_AUTO = sauvegarde["accélération_auto"]
					ACCELERER = sauvegarde["controles"]["accélérer"]
					FREINER = sauvegarde["controles"]["freiner"]
					HAUT = sauvegarde["controles"]["haut"]
					BAS = sauvegarde["controles"]["bas"]
					
					keys = pygame.key.get_pressed()
					
					if keys[FREINER]:
						self.voiture_joueur.freiner()
					elif (ACCELERATION_AUTO) or (not ACCELERATION_AUTO and keys[ACCELERER]):
						self.voiture_joueur.accelerer()
					else:
						self.voiture_joueur.ralentir(self.fps)
					if keys[HAUT]:
						self.voiture_joueur.moveUp()
					if keys[BAS]:
						self.voiture_joueur.moveDown()
					
					event = pygame.event.poll()
					self.jeu.quitter = self.quitter_partie = self.partie_finie = fermer_fenetre()
					screenshot(event, fenetre)
					
					if (event.type == KEYUP and event.key == K_ESCAPE) \
					or (event.type == JOYBUTTONUP and event.button == controller.START):
						self.afficher_pause(options)
						tps_perdu = time.time() - self.depart_tps_pause
						self.tps_perdu_chrono += tps_perdu
						self.compte_a_rebours = self.chrono + 3
				
				# Calculs
				if not self.pause:
					self.update_jeu()
				elif self.chrono >= self.compte_a_rebours:
					self.pause = False
					tps_perdu = time.time() - self.depart_tps_pause
					self.tps_perdu_100 += tps_perdu
					self.tps_perdu_sens_inverse += tps_perdu
				
				#Chrono
				self.chrono = time.time() - self.depart_chrono - self.tps_perdu_chrono
			
			if not self.pause and not self.jeu.quitter:
				self.partie_terminee()
	
	def init_gameplay(self, voiture):
		#Valeurs
		self.fps = 60
		pixel_par_sec = 3.6 #Pour 1km/h
		
		#Infos
		self.partie_finie = self.pause = False
		self.score = 0
		self.chrono = 0
		self.compteur_infos = self.compteur = self.compte_a_rebours = 3
		self.depart_chrono = time.time()
		self.depart_tps_100 = self.depart_tps_sens_inverse = 0
		self.tps_au_dessus_de_100km_h = 0
		self.tps_dans_le_sens_inverse = 0
		self.tps_au_dessus_de_100km_h_au_total = 0
		self.tps_dans_le_sens_inverse_au_total = 0
		self.tps_perdu_100 = self.tps_perdu_chrono = self.tps_perdu_sens_inverse = 0
		self.distance_parcourue = 0 #km
		self.unité_de_distance = 1/(3600 * self.fps) #(en km) Pour 1km/h
		self.pixel_par_boucle = pixel_par_sec / self.fps
		self.infos = {k:0 for k in ["score", "vitesse", "distance", "100", "contraire"]}
		
		# Lignes de démarquations
		self.lignes_blanches = []
		self.bandes_blanches = []
		self.width_bande_blanche = 50 #px
		self.height_ligne_blanche = 10 #px
		ecart_entre_chaque_ligne_blanche = 70 #px
		self.ecart_entre_chaque_bande_blanche = 20 #px
		for i in range(5):
			if not i % 2:
				if i == 0:
					y = ecran.centery - (self.height_ligne_blanche + ecart_entre_chaque_ligne_blanche)*2
				elif i == 4:
					y = ecran.centery + (self.height_ligne_blanche + ecart_entre_chaque_ligne_blanche)*2
				else:
					y = ecran.centery
				self.lignes_blanches.append(pygame.Rect(ecran.left, y, ecran.width, self.height_ligne_blanche))
			else:
				ligne = ecran.left+10
				if i == 1:
					y = ecran.centery - (self.height_ligne_blanche + ecart_entre_chaque_ligne_blanche)
				else:
					y = ecran.centery + (self.height_ligne_blanche + ecart_entre_chaque_ligne_blanche)
				bandes = []
				while ligne < ecran.right:
					bandes.append(pygame.Rect(ligne, y, self.width_bande_blanche, self.height_ligne_blanche))
					ligne += self.width_bande_blanche + self.ecart_entre_chaque_bande_blanche
				self.bandes_blanches.append(bandes)
		
		self.position_vehicule = lambda n: (self.lignes_blanches[0].bottom + 5) + (self.height_ligne_blanche + ecart_entre_chaque_ligne_blanche) * n
		
		#Voitures
		self.voiture_perso = pygame.sprite.GroupSingle()
		self.voitures_traffic = pygame.sprite.Group()
		
		# Initialiser l'emplacement du vehicule
		self.voiture_joueur = VoiturePerso(voiture, self.fps, grp=self.voiture_perso, x=ecran.left+50, centery=self.lignes_blanches[1].centery)
		self.limite_haut = self.lignes_blanches[0].bottom + 5 # Butée du haut
		self.limite_bas = self.lignes_blanches[2].top - 5 # Butée du bas
		
		# Les éléments environnant
		self.ecart_entre_chaque_arbre = 400
		self.env = {"haut":[], "bas":[]}
		r = pygame.Rect(ecran.topleft, (0, 0))
		while r.right < ecran.right:
			y = random.randrange(ecran.top, self.lignes_blanches[0].top - self.image_background.get_height())
			r1 = self.image_background.get_rect(x=r.right+self.ecart_entre_chaque_arbre, y=y)
			self.env["haut"].append(r1)
			
			y = random.randrange(self.lignes_blanches[2].bottom + 2, ecran.bottom - self.image_background.get_height())
			r = r1 = self.image_background.get_rect(x=r.right+self.ecart_entre_chaque_arbre, y=y)
			self.env["bas"].append(r1)
	
	def afficher_jeu(self, assombrir=False):
		clock.tick(self.fps)
		
		self.arriere_plan()
		self.afficher_infos()
		self.voiture_perso.draw(fenetre)
		self.voitures_traffic.draw(fenetre)
		
		if assombrir:
			# Assombrir l'écran
			voile_transparent(fenetre, BLACK, 175)
		
		clock.afficher(fenetre, centerx=ecran.centerx, top=ecran.top+10)
	
	def update_jeu(self, v=0):
		self.voiture_perso.update(self, v)
		self.voitures_traffic.update(self, v if v > 0 else self.voiture_joueur.vitesse)
		self.update_background(v)
		if self.chrono >= self.compte_a_rebours:
			self.update_infos()
			self.update_traffic()
		if not v:
			voiture_collision = self.detecteur_de_collision()
			if voiture_collision:
				if (self.voiture_joueur.vitesse >= self.voiture_joueur.vitesse_max * 0.45) or voiture_collision.opposé:
					self.crash(voiture_collision)
					self.partie_finie = True
				else:
					voiture_collision.kill()
					self.voiture_joueur.vitesse = 30
	
	def arriere_plan(self):		
		#Couleur de fond
		fenetre.fill(self.couleur_de_fond)
		
		#La route
		haut = self.lignes_blanches[0].top
		bas = self.lignes_blanches[2].bottom
		hauteur = bas - haut
		dessiner_rectangle(fenetre, GRAY, w=ecran.w, h=hauteur, topleft=self.lignes_blanches[0].topleft)
		for ligne in self.lignes_blanches:
			dessiner_rectangle(fenetre, WHITE, ligne)
		for bandes in self.bandes_blanches:
			for bande in bandes:
				dessiner_rectangle(fenetre, WHITE, bande)
		
		#Les éléments environnant
		for i in ["haut", "bas"]:
			for rect in self.env[i]:
				afficher_image(fenetre, self.image_background, rect)
	
	def update_background(self, vitesse=0):
		if vitesse == 0:
			vitesse = self.voiture_joueur.vitesse
		# Ligne de démarquation
		for bandes in self.bandes_blanches:
			for i in range(len(bandes)):
				bandes[i] = bandes[i].move(- vitesse * self.pixel_par_boucle, 0)
			if bandes[-1].right <= ecran.right - self.ecart_entre_chaque_bande_blanche:
				ligne = bandes[-1].right + self.ecart_entre_chaque_bande_blanche
				bandes.append(pygame.Rect(ligne, bandes[-1].top, self.width_bande_blanche, self.height_ligne_blanche))
			if bandes[0].right <= ecran.left:
				del bandes[0]
		
		# Les éléments environnant
		for a in ["haut", "bas"]:
			for i in range(len(self.env[a])):
				self.env[a][i] = self.env[a][i].move(- vitesse * self.pixel_par_boucle, 0)
			if self.env[a][-1].right <= ecran.right - self.ecart_entre_chaque_arbre:
				if a == "haut":
					y = random.randrange(ecran.top, self.lignes_blanches[0].top - self.image_background.get_height())
				else:
					y = random.randrange(self.lignes_blanches[2].bottom + 2, ecran.bottom - self.image_background.get_height())
				r = self.image_background.get_rect(x=ecran.right, y=y)
				self.env[a].append(r)
			if self.env[a][0].right <= 0:
				del self.env[a][0]
	
	def afficher_infos(self):
		#Score
		a = afficher_texte(fenetre, "Score", self.gameplay_font, color=YELLOW, shadow=True, topleft=(ecran.left+10, ecran.top+10))
		couleur_score = DARK_GREEN if self.score > 0 and (self.voiture_joueur.vitesse >= 100 or self.tps_dans_le_sens_inverse > 0) else YELLOW
		couleur_ombre = YELLOW if self.score > 0 and (self.voiture_joueur.vitesse >= 100 or self.tps_dans_le_sens_inverse > 0) else BLACK
		a = afficher_texte(fenetre, self.infos["score"], self.gameplay_font, color=couleur_score, shadow=True, shadow_color=couleur_ombre, x=a.x, y=a.bottom-15)
		
		#Temps au dessus de 100 km/h
		if self.voiture_joueur.vitesse >= 100:
			a = afficher_texte(fenetre, "Haute vitesse", self.gameplay_font, color=YELLOW, shadow=True, topleft=(a.x, a.bottom+25))
			a = afficher_texte(fenetre, self.infos["100"][0], self.gameplay_font, color=YELLOW, shadow=True, x=a.x, y=a.bottom-5)
		
		#Vitesse
		a = afficher_texte(fenetre, "Vitesse", self.gameplay_font, color=YELLOW, shadow=True, topright=(ecran.right - 10, ecran.top+10))
		a = afficher_texte(fenetre, "km/h", self.gameplay_font, color=YELLOW, shadow=True, right=a.right, y=a.bottom-15)
		a = afficher_texte(fenetre, self.infos["vitesse"], self.gameplay_font, color=YELLOW, shadow=True, right=a.left, y=a.top)
		
		#Distance parcourue
		a = afficher_texte(fenetre, "Distance parcourue", self.gameplay_font, color=YELLOW, shadow=True, topright=(ecran.right - 10, a.bottom+25))
		a = afficher_texte(fenetre, "km", self.gameplay_font, color=YELLOW, shadow=True, topright=(a.right, a.bottom-15))
		a = afficher_texte(fenetre, self.infos["distance"], self.gameplay_font, color=YELLOW, shadow=True, topright=(a.left, a.top))
		
		#Temps dans le sens inverse
		if self.voiture_joueur["bottom"] <= ecran.centery:
			a = afficher_texte(fenetre, "Sens contraire", self.gameplay_font, color=YELLOW, shadow=True, topleft=(ecran.left+10, self.lignes_blanches[2].bottom+10))
			a = afficher_texte(fenetre, self.infos["contraire"][0], self.gameplay_font, color=YELLOW, shadow=True, x=a.x, y=a.bottom-5)
	
	def update_infos(self):
		#Score
		if self.voiture_joueur.vitesse > 30:
			score = 1
			self.score += self.voiture_joueur.vitesse * (score / self.fps)
			if self.voiture_joueur.vitesse >= 100:
				self.score += 150 / self.fps
			if self.tps_dans_le_sens_inverse > 0:
				self.score += 120 / self.fps
		
		#Distance parcourue
		self.distance_parcourue += self.voiture_joueur.vitesse * self.unité_de_distance
		
		#Temps au dessus de 100 km/h
		if self.voiture_joueur.vitesse >= 100:
			if not self.depart_tps_100:
				self.depart_tps_100 = time.time()
			self.tps_au_dessus_de_100km_h = time.time() - self.depart_tps_100 - self.tps_perdu_100
		else:
			self.tps_au_dessus_de_100km_h_au_total += self.tps_au_dessus_de_100km_h
			self.tps_au_dessus_de_100km_h = self.tps_perdu_100 = self.depart_tps_100 = 0
		
		#Temps dans le sens inverse
		if self.voiture_joueur["bottom"] <= ecran.centery:
			if not self.depart_tps_sens_inverse:
				self.depart_tps_sens_inverse = time.time()
			self.tps_dans_le_sens_inverse = time.time() - self.depart_tps_sens_inverse - self.tps_perdu_sens_inverse
		else:
			self.tps_dans_le_sens_inverse_au_total += self.tps_dans_le_sens_inverse
			self.tps_dans_le_sens_inverse = self.tps_perdu_sens_inverse = self.depart_tps_sens_inverse = 0
		
		self.infos["score"] = round(self.score)
		self.infos["vitesse"] = round(self.voiture_joueur.vitesse)
		self.infos["distance"] = round(self.distance_parcourue, 2)
		self.infos["100"] = round(self.tps_au_dessus_de_100km_h, 1), round(self.tps_au_dessus_de_100km_h_au_total, 1)
		self.infos["contraire"] = round(self.tps_dans_le_sens_inverse, 1), round(self.tps_dans_le_sens_inverse_au_total, 1)
		
	def add_car_to_traffic(self):
		
		min = 1 #sec
		max = 2 #sec
		
		P = (max - min)*100 / 280
		ratio = max - (self.voiture_joueur.vitesse * P / 100)
		
		car_list = self.voitures_traffic.sprites()
		
		if self.chrono >= self.compteur:
			self.compteur += ratio
			if (len(car_list) == 0 or (len(car_list) > 0 and car_list[-1]["right"] < ecran.right-5)) and (self.voiture_joueur.vitesse > 30):
				if self.score >= 25000:
					nbre_de_voitures = 3
				elif self.score >= 10000:
					nbre_de_voitures = 2
				else:
					nbre_de_voitures = 1
				r = list(range(4))
				for loop in range(nbre_de_voitures):
					numero_voiture = random.randint(1,4)
					v = (35, 35, 40, 50)[numero_voiture - 1]
					
					voie = random.choice(r)
					r.remove(voie)
					
					VoitureTraffic(numero_voiture, voie, y=self.position_vehicule(voie), vitesse=v, x=ecran.right, grp=self.voitures_traffic)
	
	def update_traffic(self):
		
		self.add_car_to_traffic()
		
		voies = [list() for i in range(4)]
		
		for sprite in self.voitures_traffic:
			voies[sprite.voie].append(sprite)
		
		for k, voie in enumerate(voies, 1):
			for i in range(1, len(voie)):
				sprite_1 = voie[i-1]
				sprite_2 = voie[i]
				if sprite_2["left"] - sprite_1["right"] < 20:
					if (k in [1, 2]) and (sprite_1.vitesse < sprite_2.vitesse):
						sprite_2.vitesse = sprite_1.vitesse
					elif (k in [3, 4]) and (sprite_1.vitesse > sprite_2.vitesse):
						sprite_1.vitesse = sprite_2.vitesse
			try:
				voiture = voie[0]
			except IndexError:
				continue
			else:
				if voiture["right"] <= ecran.left:
					self.voitures_traffic.remove(voiture)
	
	def detecteur_de_collision(self):
		sprite_collision = pygame.sprite.spritecollideany(self.voiture_joueur, self.voitures_traffic, pygame.sprite.collide_mask)
		return sprite_collision
	
	def crash(self, voiture_collision):
		vitesse_vehicule_au_moment_du_crash = self.voiture_joueur.vitesse
		self.voiture_joueur.vitesse = voiture_collision.vitesse = 0 #km/h
		self.voiture_joueur.opposé = voiture_collision.opposé
		sons.play("crash")
		while (voiture_collision["right"] > ecran.left) or (self.voiture_joueur["right"] > ecran.left):
			
			self.afficher_jeu()
			
			try:
				point_de_collision = list(pygame.sprite.collide_mask(self.voiture_joueur, voiture_collision))
			except TypeError:
				pass
			else:
				point_de_collision[0] += self.voiture_joueur["x"]
				point_de_collision[1] += self.voiture_joueur["y"]
				afficher_image(fenetre, self.image_explosion, center=point_de_collision)
			
			pygame.display.flip()
			pygame.event.pump()
			
			self.update_jeu(vitesse_vehicule_au_moment_du_crash)
	
	"""-----------------------------------------------------------------------------------------------------------------------------"""
	
	def afficher_pause(self, options):
		self.pause = True
		
		widget = Widget()
		boutons_menu = widget.BoutonsMenu(1, 1, sens="vertical", liste=("REPRENDRE", "OPTIONS", "GARAGE", "QUITTER"), font_style="algerian", height=0.5*ecran.height)
		
		self.quitter_menu = False
		self.depart_tps_pause = time.time()
		
		while not self.quitter_menu:
			
			self.afficher_jeu(True)
			boutons_menu.afficher(center=ecran.center)
			pygame.display.flip()
			
			event = pygame.event.poll()
			widget[event]
			choix = boutons_menu.event()
			self.jeu.quitter = self.quitter_partie = self.partie_finie = fermer_fenetre()
			screenshot(event, fenetre)
			
			#Option 'REPRENDRE'
			if choix == 1:
				self.quitter_menu = True
			
			#Option 'OPTIONS'
			if choix == 2:
				options.run(self, "gameplay", lambda: self.afficher_jeu(True), center=ecran.center)
			
			#Option 'GARAGE'
			if choix == 3:
				self.quitter_menu = self.partie_finie = self.quitter_partie = True
			
			#Option 'QUITTER'
			if choix == 4:
				self.quitter_menu = self.partie_finie = self.quitter_partie = self.jeu.quitter_garage = True
	
	def partie_terminee(self):
		widget = Widget()
		boutons_menu = widget.BoutonsMenu(1, 1, sens="horizontal", liste=("RECOMMENCER", "GARAGE", "MENU"), font_style="algerian", width=0.90*ecran.width)
		
		#Calcul de l'argent obtenue en tout
		argent_distance = round(300.40 * self.distance_parcourue)
		argent_tps_100_kmh = round(12.5 * self.tps_au_dessus_de_100km_h_au_total)
		argent_tps_sens_inverse = round(21.7 * self.tps_dans_le_sens_inverse_au_total)
		somme_totale = argent_distance + argent_tps_100_kmh + argent_tps_sens_inverse
		if sauvegarde["argent"] + somme_totale < 10**9:
			sauvegarde["argent"] += somme_totale
		else:
			sauvegarde["argent"] = 10**9 - 1
		
		#Score
		if self.infos["score"] > sauvegarde["meilleur_score"]:
			sauvegarde["meilleur_score"] = self.infos["score"]
			new_high_score = True
		else:
			new_high_score = False		
		score_font = fonts("algerian", 120)
		money_font = fonts("calibri", 50)
		donnees_font = fonts("calibri", 50)
		while True:
			
			#Afficher le jeu
			self.afficher_jeu(True)
			
			#Argent totale
			piece = afficher_image(fenetre, self.piece, size=(35, 35), right=ecran.right-5, top=ecran.top+5)
			afficher_texte(fenetre, sauvegarde["argent"], money_font, color=YELLOW, right=piece.left-4, centery=piece.centery)
			
			#Score
			score = afficher_texte(fenetre, self.infos["score"], score_font, color=YELLOW, centerx=ecran.centerx, centery=ecran.top+0.25*ecran.height)
			score = afficher_texte(fenetre, "Votre score", score_font, color=YELLOW, centerx=ecran.centerx, bottom=score.top)
			if new_high_score:
				afficher_image(fenetre, self.image_nouveau_meilleur_score,left=score.right-10, bottom=score.top+100)
			
			#Argent gagnée
			taille_piece = (40, 40) #px
			cadre = dessiner_rectangle(fenetre, BLACK, w=0.75*ecran.w, h=0.45*ecran.h, centerx=ecran.centerx, top=0.75*ecran.centery, outline=1, outline_color=WHITE)
			#--- Distance parcourue
			d_p = afficher_texte(fenetre, "Distance parcourue: ", donnees_font, x=cadre.x+5, y=cadre.y+5, color=YELLOW)
			d_p = afficher_texte(fenetre, self.infos["distance"], donnees_font, color=YELLOW, x=d_p.right, y=d_p.y)
			d_p = afficher_image(fenetre, self.fleche_verte, x=cadre.centerx+75, centery=d_p.centery-3)
			d_p = afficher_texte(fenetre, argent_distance, donnees_font, color=YELLOW, x=d_p.right+10, centery=d_p.centery+3)
			d_p = afficher_image(fenetre, self.piece, size=taille_piece, x=d_p.right+5, centery=d_p.centery-3)
			#--- Au dessus de 100km/h
			tps_100 = afficher_texte(fenetre, "Au dessus de 100km/h: ", donnees_font, x=cadre.x+5, y=cadre.y+75, color=YELLOW)
			tps_100 = afficher_texte(fenetre, self.infos["100"][1], donnees_font, color=YELLOW, x=tps_100.right, y=tps_100.y)
			tps_100 = afficher_image(fenetre, self.fleche_verte, x=cadre.centerx+75, centery=tps_100.centery-3)
			tps_100 = afficher_texte(fenetre, argent_tps_100_kmh, donnees_font, color=YELLOW, x=tps_100.right+10, centery=tps_100.centery+3)
			tps_100 = afficher_image(fenetre, self.piece, size=taille_piece, x=tps_100.right+5, centery=tps_100.centery-3)
			#--- Sens contraire
			tps_sens_inv = afficher_texte(fenetre, "Sens contraire: ", donnees_font, x=cadre.x+5, y=cadre.y+145, color=YELLOW)
			tps_sens_inv = afficher_texte(fenetre, self.infos["contraire"][1], donnees_font, color=YELLOW, x=tps_sens_inv.right, y=tps_sens_inv.y)
			tps_sens_inv = afficher_image(fenetre, self.fleche_verte, x=cadre.centerx+75, centery=tps_sens_inv.centery-3)
			tps_sens_inv = afficher_texte(fenetre, argent_tps_sens_inverse, donnees_font, color=YELLOW, x=tps_sens_inv.right+10, centery=tps_sens_inv.centery+3)
			tps_sens_inv = afficher_image(fenetre, self.piece, size=taille_piece, x=tps_sens_inv.right+5, centery=tps_sens_inv.centery-3)
			#--- TOTAL
			total = afficher_texte(fenetre, "TOTAL: ", donnees_font, centerx=cadre.centerx*0.90, bottom=cadre.bottom-10, color=YELLOW)
			total = afficher_texte(fenetre, somme_totale, donnees_font, color=YELLOW, x=total.right+10, centery=total.centery)
			total = afficher_image(fenetre, self.piece, size=taille_piece, x=total.right+5, centery=total.centery-3)
			
			#Options
			boutons_menu.afficher(centerx=ecran.centerx, top=cadre.bottom+10)
			
			pygame.display.flip()
			
			event = pygame.event.poll()
			widget[event]
			choix = boutons_menu.event()
			
			if fermer_fenetre():
				self.jeu.quitter = self.quitter_partie = True
				break
			screenshot(event, fenetre)
			
			#Option 'RECOMMENCER'
			if choix == 1:
				break
			
			#Option 'GARAGE'
			if choix == 2:
				self.quitter_partie = True
				break
			#Option 'MENU'
			if choix == 3:
				self.jeu.quitter_garage = self.quitter_partie = True
				break

# Création d'une classe 'Voiture' qui contient la construction type d'une voiture
class Voiture(pygame.sprite.Sprite):
	def __init__(self, sprites, opposé=False, vitesse=30, grp=None, **kwargs):
		if grp is not None:
			pygame.sprite.Sprite.__init__(self, grp)
		else:
			pygame.sprite.Sprite.__init__(self)
		
		self.sprites = sprites
		self.id = 0
		self.image = sprites[0]
		self.mask = pygame.mask.from_surface(self.image, 140)
		self.rect = self.image.get_rect(**kwargs)
		
		self.vitesse_max = self.vitesse = vitesse
		self.opposé = opposé
		self.up = False
		self.down = False
	
	@property
	def vitesse(self):
		return self.__vitesse
	
	@vitesse.setter
	def vitesse(self, v):
		if v < 30:
			self.__vitesse = 30
		elif v > self.vitesse_max:
			self.__vitesse = self.vitesse_max
		else:
			self.__vitesse = v
	
	def __setitem__(self, clé, valeur):
		self.rect = modifier_rect(self.rect, **{clé: valeur})
	
	def __getitem__(self, clé):
		return rect_value(self.rect, clé)
	
	def update(self, gameplay, v=0):
		
		# Frame Voiture
		limite = 150 #km/h
		ratio_max = 60 / gameplay.fps
		ratio_max = 1 if ratio_max > 1 else ratio_max
		coeff = ratio_max / limite
		self.ratio = self.vitesse * coeff if self.vitesse < limite else ratio_max
		self.id += self.ratio
		if int(self.id) == len(self.sprites):
			self.id = 0
		self.image = self.sprites[int(self.id)]
		
		# Deplacement verticale
		try:
			y = (self.maniabilité)/2 if self.vitesse < 50 else self.maniabilité
		except AttributeError:
			pass
		else:
			if self.up:
				self.rect = self.rect.move(0, -y)
				self.rect.top = gameplay.limite_haut if self.rect.top < gameplay.limite_haut else self.rect.top
			if self.down:
				self.rect = self.rect.move(0, y)
				self.rect.bottom = gameplay.limite_bas if self.rect.bottom > gameplay.limite_bas else self.rect.bottom
			self.up = False
			self.down = False
		
		# Déplacement horizontal
		if v > 0:
			x = self.vitesse * gameplay.pixel_par_boucle if not self.opposé else self.vitesse * (-gameplay.pixel_par_boucle)
			x -= v * gameplay.pixel_par_boucle
			self.rect = self.rect.move(x, 0)

# Création de la classe 'VoiturePerso' qui est la voiture du joueur
class VoiturePerso(Voiture):
	def __init__(self, voiture, fps, **kwargs):
		Voiture.__init__(self, images["voitures_joueur"][voiture], **kwargs)
		
		v = infos_vehicules[voiture]["vitesse_max"]
		a = infos_vehicules[voiture]["accélération"]
		m = infos_vehicules[voiture]["maniabilité"]
		f = infos_vehicules[voiture]["freinage"]
		
		self.vitesse_max = v
		self.acceleration = 100/ (a * fps)
		self.maniabilité = m / fps
		self.freinage = v /(f * fps)
	
	def accelerer(self):
		self.vitesse += self.acceleration
	
	def freiner(self):
		self.vitesse -= self.freinage
	
	def ralentir(self, fps):
		ratio = 5 # % de vitesse perdu par secondes
		self.vitesse *= (1 - (ratio / (100*fps)))
	
	def moveUp(self):
		self.up = True
	
	def moveDown(self):
		self.down = True
	

# Création de la classe 'VoitureTraffic' qui est la voiture rencontré sur
# la route et servant d'obstacle
class VoitureTraffic(Voiture):
	def __init__(self, voiture, voie, **kwargs):
		if voie < 2:
			sens = "opposé"
			opposé = True
		else:
			sens = "normal"
			opposé = False
		Voiture.__init__(self, images["voitures_traffic"][sens][voiture], opposé, **kwargs)
		self.voie = voie