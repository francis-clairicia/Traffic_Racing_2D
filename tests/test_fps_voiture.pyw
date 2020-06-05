# -*- coding: Utf-8 -*

import os
import sys
import time
import pygame
os.chdir(os.path.join(os.path.dirname(sys.path[0]), "files", "img", "gameplay"))

pygame.init()

# Création d'une classe 'Voiture' qui contient la construction type d'une voiture
class VoiturePerso(pygame.sprite.Sprite):
    def __init__(self, numero_voiture: int):
        pygame.sprite.Sprite.__init__(self)

        self.sprites = []
        self.load(numero_voiture)
        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.time_elapsed = 0
        self.id = 0
        self.ratio = 10
        self.nb_frames_to_skip = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()

    def load(self, numero_voiture: int):
        self.sprites.clear()
        for i in range(10):
            i += 1
            try:
                img = pygame.image.load(f"voiture_{numero_voiture}/{i}.png").convert_alpha()
            except (pygame.error, FileNotFoundError):
                continue
            else:
                self.sprites.append(img)

    def elapsed_time(self, milliseconds: float) -> bool:
        self.time_elapsed += self.clock.tick()
        if self.time_elapsed >= milliseconds:
            self.time_elapsed = 0
            return True
        return False

    def update(self, *args):
        surface = args[0]
        surface_rect = surface.get_rect()

        # Frame Voiture
        if self.elapsed_time(self.ratio):
            self.id += 1 + self.nb_frames_to_skip
            self.id %= len(self.sprites)
            self.image = self.sprites[int(self.id)]
        self.rect = self.image.get_rect(center=surface_rect.center)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# couleurs
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (170, 255, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (16, 156, 0)
LIGHT_BLUE = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (165, 0, 255)
PINK = (255, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (145, 145, 145)

def main():
    done = False

    taille_ecran = (1000, 600)
    fenetre = pygame.display.set_mode(taille_ecran)
    clock = pygame.time.Clock()
    pygame.key.set_repeat(100, 50)

    # Police
    myfont = pygame.font.SysFont("calibri", 35)

    numero_voiture = {
        pygame.K_KP1: 1,
        pygame.K_KP2: 2,
        pygame.K_KP3: 3,
        pygame.K_KP4: 4,
        pygame.K_KP5: 5,
        pygame.K_KP6: 6,
        pygame.K_KP7: 7,
        pygame.K_KP8: 8,
        pygame.K_KP9: 9
    }

    voiture_joueur = VoiturePerso(6)

    depart = time.time()
    couleur_de_fond = BLACK
    fps = 60
    r = True

    while not done:
        clock.tick(fps)

        fenetre.fill(couleur_de_fond)
        minuteur = time.time() - depart

        heures = int(minuteur)//3600
        minutes = int(minuteur)//60
        secondes = int(minuteur)%60
        millièmes = int((minuteur - int(minuteur))*1000)
        texte_tps = myfont.render(f"Chrono: {heures:02}:{minutes:02}:{secondes:02}:{millièmes:03}", 1, BLUE)
        texte_fps_set = myfont.render(f"Set: {fps}fps", 1, BLUE)
        texte_fps_gameplay = myfont.render(f"GP: {int(clock.get_fps())}fps", 1, BLUE)
        texte_ratio_id_voiture = myfont.render(f"Ratio: {voiture_joueur.ratio}", 1, BLUE)
        texte_frame_skip = myfont.render(f"Num. voiture: {voiture_joueur.nb_frames_to_skip}", 1, BLUE)

        tps = fenetre.blit(texte_tps, (10, 10))
        fps_v = fenetre.blit(texte_fps_set, texte_fps_set.get_rect(x=10, y=tps.bottom))
        fps_g = fenetre.blit(texte_fps_gameplay, texte_fps_gameplay.get_rect(x=10, y=fps_v.bottom))
        ratio_r = fenetre.blit(texte_ratio_id_voiture, texte_ratio_id_voiture.get_rect(x=10, y=fps_g.bottom))
        fenetre.blit(texte_frame_skip, texte_frame_skip.get_rect(x=10, y=ratio_r.bottom))

        voiture_joueur.update(fenetre)
        voiture_joueur.draw(fenetre)

        #Rafraichissement
        pygame.display.flip()

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                fps += 1
            if keys[pygame.K_LEFT] and fps > 15:
                fps -= 1
            if keys[pygame.K_UP]:
                voiture_joueur.ratio += 10
            if keys[pygame.K_DOWN] and voiture_joueur.ratio > 10:
                voiture_joueur.ratio -= 10
            if keys[pygame.K_RETURN]:
                r = not r
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_MINUS and voiture_joueur.nb_frames_to_skip > 0:
                    voiture_joueur.nb_frames_to_skip -= 1
                if event.key == pygame.K_KP_PLUS:
                    voiture_joueur.nb_frames_to_skip += 1
                if event.key in numero_voiture:
                    voiture_joueur.load(numero_voiture[event.key])

    pygame.quit()

if __name__ == "__main__":
    main()