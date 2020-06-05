# -*- coding: Utf-8 -*

from modules.init import *
from modules.classes import *
from my_pygame.colors import *
from modules.fonctions import *

class Options:
    
    def __init__(self, jeu):
        self.jeu = jeu
        clock.show = sauvegarde["fps"]
        
        self.titre_options_font = fonts("calibri", 70)
        self.options_font = fonts("calibri", 40)
        self.case_font = fonts("calibri", 30)
        
        #Boutons / Cases à cocher/ Echelles
        self.widget = Widget()
        self.boutons = {
            "fleche_bleue": self.widget.Bouton(1, 1, tag=(1, 2), type="img", sound="retour", img=images["fleche_bleue"]),
            "fps": self.widget.Bouton(4, 1, tag=1, sound="selection", text="", text_color=WHITE, font=self.case_font, bg=(BLACK, GRAY), outline=(1, YELLOW)),
            "reset": self.widget.Bouton(5, 1, tag=1, text="OUI", text_color=WHITE, font=self.case_font, bg=(RED, RED_DARK), outline=(1, WHITE)),
            "accélération_auto": self.widget.Bouton(2, 1, tag=2, sound="selection", text="", text_color=WHITE, font=self.case_font, bg=(BLACK, GRAY), outline=(1, YELLOW)),
            "accélérer": self.widget.Bouton(2, 2, tag=2, sound="selection", text="", text_color=WHITE, font=self.case_font, bg=(BLACK, GRAY), outline=(1, YELLOW)),
            "freiner": self.widget.Bouton(3, 1, tag=2, sound="selection", text="", text_color=WHITE, font=self.case_font, bg=(BLACK, GRAY), outline=(1, YELLOW)),
            "haut": self.widget.Bouton(4, 1, tag=2, sound="selection", text="", text_color=WHITE, font=self.case_font, bg=(BLACK, GRAY), outline=(1, YELLOW)),
            "bas": self.widget.Bouton(5, 1, tag=2, sound="selection", text="", text_color=WHITE, font=self.case_font, bg=(BLACK, GRAY), outline=(1, YELLOW)),
            "page": self.widget.Bouton(6, 1, tag=(1, 2), sound="selection", text=">>", text_color=WHITE, font=self.case_font, bg=(BLACK, GRAY), outline=(1, YELLOW)),
            }
        self.cases_a_cocher = {
            "musique": self.widget.CaseACocher(2, 1, tag=1, size=30, img=images["valide_vert"], statut=sauvegarde["musique"]["etat"]),
            "sfx": self.widget.CaseACocher(3, 1, tag=1, size=30, img=images["valide_vert"], statut=sauvegarde["sfx"]["etat"])
            }
        self.barre_echelle = {
            "musique": self.widget.BarreEchelle(2, 2, tag=1, bornes=(0, 100), size=(350, 30), scale_color=DARK_GREEN, outline=(2, BLACK), depart=sauvegarde["musique"]["volume"]*100, show_value=True, font=self.options_font),
            "sfx": self.widget.BarreEchelle(3, 2, tag=1, bornes=(0, 100), size=(350, 30), scale_color=DARK_GREEN, outline=(2, BLACK), depart=sauvegarde["sfx"]["volume"]*100, show_value=True, font=self.options_font)
            }
    
    def run(self, section, nom_section, *args, **kwargs):
        self.section = section
        self.changement_options_fini = False
        self.widget.tag = self.page = 1
        while not self.changement_options_fini:
            clock.tick(60)
            self.afficher(args, kwargs)
            event = pygame.event.poll()
            self.jeu.quitter = self.section.partie_finie = self.section.quitter_partie = self.section.quitter_menu = self.changement_options_fini = fermer_fenetre()
            screenshot(event, fenetre)
            
            self.boutons["accélérer"].state = bool(sauvegarde["accélération_auto"] is False)
            self.barre_echelle["musique"].state = self.cases_a_cocher["musique"].statut
            self.barre_echelle["sfx"].state = self.cases_a_cocher["sfx"].statut
            self.widget[event]
            
            if (event.type == KEYUP and event.key == K_ESCAPE) \
            or (event.type == JOYBUTTONUP and event.button == controller.B):
                self.boutons["fleche_bleue"].clicked = True
            
            #Flèche bleue
            if self.boutons["fleche_bleue"].clicked:
                self.changement_options_fini = True
            
            #Musique
            if self.cases_a_cocher["musique"].clicked:
                sauvegarde["musique"]["etat"] = self.cases_a_cocher["musique"].statut
                sons.play(nom_section)
            if self.cases_a_cocher["musique"].statut is True:
                volume = self.barre_echelle["musique"].pourcentage
                sauvegarde["musique"]["volume"] = volume
                sons.volume_music(volume)
            #SFX
            if self.cases_a_cocher["sfx"].clicked:
                sauvegarde["sfx"]["etat"] = self.cases_a_cocher["sfx"].statut
            if self.cases_a_cocher["sfx"].statut is True:
                volume = self.barre_echelle["sfx"].pourcentage
                sauvegarde["sfx"]["volume"] = volume
                sons.volume_sfx(volume)
            #Accélération auto
            if self.boutons["accélération_auto"].clicked:
                sauvegarde["accélération_auto"] = not sauvegarde["accélération_auto"]
            #Touche pour accélérer
            if self.boutons["accélérer"].clicked:
                afficher_texte(fenetre, "Echap: Annuler", self.case_font, x=self.boutons["accélérer"].rect.right+3, centery=self.boutons["accélérer"].rect.centery)
                pygame.display.update()
                self.changer_hotkey("accélérer")
            #Touche pour freiner
            if self.boutons["freiner"].clicked:
                afficher_texte(fenetre, "Echap: Annuler", self.case_font, x=self.boutons["freiner"].rect.right+3, centery=self.boutons["freiner"].rect.centery)
                pygame.display.update()
                self.changer_hotkey("freiner")
            #Touche pour aller en haut
            if self.boutons["haut"].clicked:
                afficher_texte(fenetre, "Echap: Annuler", self.case_font, x=self.boutons["haut"].rect.right+3, centery=self.boutons["haut"].rect.centery)
                pygame.display.update()
                self.changer_hotkey("haut")
            self.couleur_haut = BLACK
            #Touche pour aller en bas
            if self.boutons["bas"].clicked:
                afficher_texte(fenetre, "Echap: Annuler", self.case_font, x=self.boutons["bas"].rect.right+3, centery=self.boutons["bas"].rect.centery)
                pygame.display.update()
                self.changer_hotkey("bas")
            
            if self.boutons["fps"].clicked:
                clock.show = sauvegarde["fps"] = not sauvegarde["fps"]
            if self.boutons["reset"].clicked:
                sauvegarde.reset()
            
            #Changement de page
            if self.boutons["page"].clicked:
                self.page = 2 if self.page == 1 else 1
                self.widget.tag = self.page
    
    def afficher(self, args, kwargs):
        ##################
        for arriere_plan in args:
            arriere_plan()
        ##################
        cadre_options = dessiner_rectangle(fenetre, GREEN_LIGHT, outline=4, outline_color=BLACK, size=(760, 420), **kwargs)
        
        self.boutons["fleche_bleue"].afficher(left=cadre_options.left+5, top=cadre_options.top+5)
        
        titre_options = afficher_texte(fenetre, "OPTIONS", self.titre_options_font, centerx=cadre_options.centerx, top=cadre_options.top+10)
        
        ######## PAGE 1 ########
        if self.page == 1:
            musique = afficher_texte(fenetre, "Musique:", self.options_font, left=cadre_options.left+10, top=titre_options.bottom+10)
            case_a_cocher_musique = self.cases_a_cocher["musique"].afficher(x=musique.right+10, centery=musique.centery)
            if self.cases_a_cocher["musique"].statut is True:
                self.barre_echelle["musique"].afficher(x=case_a_cocher_musique.right+50, centery=musique.centery)
            
            sfx = afficher_texte(fenetre, "Sons:", self.options_font, right=musique.right, top=musique.bottom+5)
            case_a_cocher_sfx = self.cases_a_cocher["sfx"].afficher(x=musique.right+10, centery=sfx.centery)
            if sauvegarde["sfx"]["etat"] is True:
                self.barre_echelle["sfx"].afficher(x=case_a_cocher_sfx.right+50, centery=sfx.centery)
            
            fps_button = afficher_texte(fenetre, "FPS:", self.options_font, left=cadre_options.left+10, top=cadre_options.centery+30)
            self.boutons["fps"].text = "Affiché" if sauvegarde["fps"] else "Masqué"
            self.boutons["fps"].afficher(x=fps_button.right+10, centery=fps_button.centery, size=(120, 40))
            reset = afficher_texte(fenetre, "Réinitialiser:", self.options_font, left=cadre_options.left+10, top=fps_button.bottom+10)
            self.boutons["reset"].afficher(x=reset.right+10, centery=reset.centery, size=(120, 40))
        
        ######## PAGE 2 ########	
        elif self.page == 2:
            
            accélérer = afficher_texte(fenetre, "Accélérer:", self.options_font, (cadre_options.left+10, titre_options.bottom+30))
            self.boutons["accélération_auto"].text = "Automatique" if sauvegarde["accélération_auto"] else "Manuel"
            accélération_auto = self.boutons["accélération_auto"].afficher(x=accélérer.right+10, centery=accélérer.centery, height=40)
            if sauvegarde["accélération_auto"] is False:
                touche = afficher_texte(fenetre, "Touche:", self.options_font, left=accélération_auto.right+10, centery=accélérer.centery)
                self.boutons["accélérer"].text = clavier[sauvegarde["controles"]["accélérer"]]
                self.boutons["accélérer"].afficher(x=touche.right+10, centery=accélérer.centery, size=(120, 40))
            
            ecart = 10
            
            freiner = afficher_texte(fenetre, "Freiner:", self.options_font, (cadre_options.left+10, accélérer.bottom+ecart))
            self.boutons["freiner"].text = clavier[sauvegarde["controles"]["freiner"]]
            self.boutons["freiner"].afficher(x=freiner.right+10, centery=freiner.centery, size=(120, 40))
            
            haut = afficher_texte(fenetre, "Aller en haut:", self.options_font, (cadre_options.left+10, freiner.bottom+ecart))
            self.boutons["haut"].text = clavier[sauvegarde["controles"]["haut"]]
            self.boutons["haut"].afficher(x=haut.right+10, centery=haut.centery, size=(120, 40))
            
            bas = afficher_texte(fenetre, "Aller en bas:", self.options_font, (cadre_options.left+10, haut.bottom+ecart))
            self.boutons["bas"].text = clavier[sauvegarde["controles"]["bas"]]
            self.boutons["bas"].afficher(x=bas.right+10, centery=bas.centery, size=(120, 40))
        
        self.boutons["page"].afficher(bottom=cadre_options.bottom-5, right=cadre_options.right-5)
        pygame.display.flip()
    
    def changer_hotkey(self, controle):
        while True:
            event = pygame.event.poll()
            if fermer_fenetre(event):
                self.changement_options_fini = True
                self.section.quitter_menu = True
                self.jeu.quitter = True
                self.section.quitter_partie = True
                self.section.partie_finie = True
                break
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    break
                elif event.key in clavier:
                    for c in sauvegarde["controles"].keys():
                        if sauvegarde["controles"][c] == event.key:
                            sauvegarde["controles"][c] = None
                    sauvegarde["controles"][controle] = event.key
                    break