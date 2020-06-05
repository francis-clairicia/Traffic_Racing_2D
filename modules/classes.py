# -*- coding: Utf-8 -*

from modules.init import *

class Widget:
    
    def __init__(self):
        self.w = {}
        self.max_ligne = {}
        self.max_colonne = {}
        self.ligne = 1
        self.colonne = 1
        self.tag = None

    def __getitem__(self, event):
        if (event.type == KEYDOWN and event.key == K_UP) \
        or (event.type == JOYHATMOTION and event.value == controller.UP):
            try:
                while True:
                    if self.ligne > 1:
                        self.ligne -= 1
                    else:
                        self.ligne = self.max_ligne[self.tag]["max"]
                    if not all(not w.state for w in self.w[self.tag][self.ligne, self.colonne]):
                        break
            except KeyError:
                pass
            while self.colonne > self.max_colonne[self.tag][self.ligne]:
                self.colonne -= 1
        elif (event.type == KEYDOWN and event.key == K_DOWN) \
        or (event.type == JOYHATMOTION and event.value == controller.DOWN):
            try:
                while True:
                    if self.ligne < self.max_ligne[self.tag]["max"]:
                        self.ligne += 1
                    else:
                        self.ligne = 1
                    if not all(not w.state for w in self.w[self.tag][self.ligne, self.colonne]):
                        break
            except KeyError:
                pass
            while self.colonne > self.max_colonne[self.tag][self.ligne]:
                self.colonne -= 1
        elif (event.type == KEYDOWN and event.key == K_LEFT) \
        or (event.type == JOYHATMOTION and event.value == controller.LEFT):
            try:
                while True:
                    if self.colonne > 1:
                        self.colonne -= 1
                    elif self.ligne > 0:
                        self.colonne = self.max_colonne[self.tag][self.ligne]
                    else:
                        self.colonne = 1
                    if not all(not w.state for w in self.w[self.tag][self.ligne, self.colonne]):
                        break
            except KeyError:
                pass
        elif (event.type == KEYDOWN and event.key == K_RIGHT) \
        or (event.type == JOYHATMOTION and event.value == controller.RIGHT):
            try:
                while True:
                    if self.colonne < self.max_colonne[self.tag][self.ligne]:
                        self.colonne += 1
                    else:
                        self.colonne = 1
                    if not all(not w.state for w in self.w[self.tag][self.ligne, self.colonne]):
                        break
            except KeyError:
                pass
        
        event_list = [KEYDOWN, KEYUP, JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP]
        for cellule, w in self.w[self.tag].items():
            for widget in w:
                widget.input = bool(cellule == (self.ligne, self.colonne))
                if event.type != NOEVENT:
                    widget.keyboard_controller_input = bool(event.type in event_list)
                    widget[event]
                    if event.type == KEYUP or event.type == MOUSEBUTTONUP:
                        widget.active = False
    
    @property
    def tag(self):
        return self.__tag
    
    @tag.setter
    def tag(self, tag):
        if (tag is None) or (str(tag) in self.w.keys()):
            self.__tag = str(tag)
        if str(tag) in self.w.keys():
            while self.ligne > self.max_ligne[self.tag]["max"]:
                self.ligne -= 1
            if self.ligne > 0:
                while self.colonne > self.max_colonne[self.tag][self.ligne]:
                    self.colonne -= 1
    
    """----------------------------------------------------------------------------------------"""
    
    def create(self, classe, ligne, colonne, tag, kwargs):
        ligne = 1 if ligne <= 0 else ligne
        colonne = 1 if colonne <= 0 else colonne
        
        if isinstance(tag, (tuple, list)):
            tags = [str(t) for t in tag]
        else:
            tags = [str(tag)]
        
        if classe is not BoutonsMenu:
            w = classe([self, ligne, colonne], **kwargs)
        else:
            w = classe(**kwargs)
        
        for tag in tags:
            if not tag in self.w:
                self.w[tag] = {}
            if not tag in self.max_ligne:
                self.max_ligne[tag] = {}
            if not tag in self.max_colonne:
                self.max_colonne[tag] = {}
            cellule = [ligne, colonne]
            if classe is not BoutonsMenu:
                if tuple(cellule) not in self.w[tag]:
                    self.w[tag][tuple(cellule)] = [w]
                elif tuple(cellule) in self.w[tag]:
                    self.w[tag][tuple(cellule)].append(w)
                self.max_ligne[tag][colonne] = max([0] + [l for l, c in self.w[tag] if c == colonne])
                self.max_colonne[tag][ligne] = max([0] + [c for l, c in self.w[tag] if l == ligne])
            else:
                for b in w:
                    if tuple(cellule) not in self.w[tag]:
                        self.w[tag][tuple(cellule)] = [b]
                    elif tuple(cellule) in self.w[tag]:
                        self.w[tag][tuple(cellule)].append(b)
                    b.widget_manager = self
                    b.ligne, b.colonne = cellule
                    self.max_ligne[tag][cellule[1]] = max([0] + [l for l, c in self.w[tag] if c == cellule[1]])
                    self.max_colonne[tag][cellule[0]] = max([0] + [c for l, c in self.w[tag] if l == cellule[0]])
                    cellule[0] += 1 if w.sens == "vertical" else 0
                    cellule[1] += 1 if w.sens == "horizontal" else 0
            self.max_ligne[tag]["max"] = max([l for l, c in self.w[tag]])
        return w
    
    def Bouton(self, ligne, colonne, tag=None, **kwargs):
        return self.create(Bouton, ligne, colonne, tag, kwargs)
    
    def BoutonsMenu(self, ligne, colonne, tag=None, **kwargs):
        return self.create(BoutonsMenu, ligne, colonne, tag, kwargs)
    
    def CaseACocher(self, ligne, colonne, tag=None, **kwargs):
        return self.create(CaseACocher, ligne, colonne, tag, kwargs)
    
    def BarreEchelle(self, ligne, colonne, tag=None, **kwargs):
        return self.create(BarreEchelle, ligne, colonne, tag, kwargs)

class Objet:
    
    def __init__(self, info_widget, button=False, validate_key=None, validate_button=None):
        self.button = button
        self.widget_manager, self.ligne, self.colonne = info_widget
        self.active = self.input = self.keyboard_controller_input = False
        self.validate_key = validate_key if isinstance(validate_key, int) else K_RETURN
        self.validate_button = validate_button if isinstance(validate_button, str) else "A"
        self.clicked = False
        self.state = True
    
    def __getitem__(self, event):
        if self.state:
            self.events(event)
    
    def events(self, event):
        self.mouse_event(event)
        if self.input and self.keyboard_controller_input:
            self.keyboard_controller_event(event)
    
    def mouse_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == MOUSEMOTION and self.rect.collidepoint(mouse_pos):
            self.widget_manager.ligne = self.ligne
            self.widget_manager.colonne = self.colonne
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(mouse_pos)
        
        if event.type == MOUSEBUTTONUP and event.button == 1 and self.active:
            self.active = False
            if self.rect.collidepoint(mouse_pos):
                self.clicked = True
    
    def keyboard_controller_event(self, event):
        if (event.type == KEYDOWN and event.key == self.validate_key) \
        or (event.type == JOYBUTTONDOWN and event.button == controller.value(self.validate_button)):
                self.active = True
        
        if (event.type == KEYUP and event.key == self.validate_key) \
        or (event.type == JOYBUTTONUP and event.button == controller.value(self.validate_button)):
            if self.active:
                self.active = False
                self.clicked = True
    
    @property
    def clicked(self):
        c = self.__clicked
        self.__clicked = False
        if c:
            sons.play(self.sound)
        return c
    
    @clicked.setter
    def clicked(self, value):
        self.__clicked = bool(value)
    
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, s):
        self.__state = bool(s)
        
    @property
    def input(self):
        return self.__input
    
    @input.setter
    def input(self, value):
        self.__input = value
        if value:
            if not self.button or (self.button and self.shown_bg):
                self.outline_color = YELLOW
                self.outline = 4
            else:
                self.outline = 2
        else:
            if not self.button or (self.button and self.shown_bg):
                self.outline_color = self.default_outline_color
                self.outline = self.default_outline
            else:
                self.outline = 0
    
    @property
    def active(self):
        return self.__active
    
    @active.setter
    def active(self, active):
        self.__active = active
        if self.button:
            if active:
                if self.type == "img":
                    self.img = self.image_hover
                if self.shown_bg:
                    self.couleur_arriere_plan = self.background[1]
            else:
                if self.type == "img":
                    self.img = self.image
                if self.shown_bg:
                    self.couleur_arriere_plan = self.background[0]

class BoutonsMenu:
    
    def __init__(self, sens, liste, font_style="calibri", font_size=20, width=0, height=0):
        # Informations nécessaires à la création des options
        self.sens = sens
        if width:
            w = 0
            font_size = 0
            while w < width: 
                font_size += 2
                w, h = self.init(liste, font_style, font_size)
        elif height:
            h = 0
            font_size = 0
            while h < height: 
                font_size += 2
                w, h = self.init(liste, font_style, font_size)
        else:
            self.init(liste, font_style, font_size)
    
    def init(self, liste, font_style, font_size):
        #Polices d'écriture
        menu_font = fonts(font_style, font_size)
        word_size_list = {"width":[], "height":[]}
        # Création d'une liste qui va sauvegarder les informations pour chaque options
        self.options = []
        for element in liste:
            element = str(element)
            b = Bouton([None for i in range(3)], text=element, font=menu_font)
            self.options.append(b)
            word_size_list["width"].append(b.rect.width)
            word_size_list["height"].append(b.rect.height)
        w, h = self.taille_option = max(word_size_list["width"]), max(word_size_list["height"])
        nbre_d_options = len(self.options)
        self.ecart_entre_les_cases = 20
        if self.sens == "vertical":
            h = h * nbre_d_options + self.ecart_entre_les_cases * (nbre_d_options-1)
        elif self.sens == "horizontal":
            w = w * nbre_d_options + self.ecart_entre_les_cases * (nbre_d_options-1)
        self.rect = pygame.Rect(0, 0, w, h)
        return w, h
    
    def __iter__(self):
        return iter(self.options)
    
    @property
    def sens(self):
        return self.__sens
    
    @sens.setter
    def sens(self, sens):
        assert sens in ["horizontal", "vertical"]
        self.__sens = sens
    
    def afficher(self, **kwargs):
        for key in ["size", "width", "w", "height", "h"]:
            try:
                del kwargs[key]
            except KeyError:
                continue
        
        self.rect = modifier_rect(self.rect, **kwargs)
        
        ecart_entre_les_cases = self.ecart_entre_les_cases
        nbre_d_options = len(self.options)
        x = self.rect.left
        y = self.rect.top
        for option in self.options:
            if self.sens == "vertical":
                r = option.afficher(top=y, centerx=self.rect.centerx, size=self.taille_option)
                y = r.bottom + ecart_entre_les_cases
            elif self.sens == "horizontal":
                r = option.afficher(left=x, centery=self.rect.centery, size=self.taille_option)
                x = r.right + ecart_entre_les_cases
        
        return self.rect
    
    def event(self):
        choix = 0
        for i, option in enumerate(self.options, 1):
            if option.clicked:
                choix = i
        return choix

class Bouton(Objet):
    
    def __init__(self, info_widget, type="default", sound="validation", img=None, text=None, shown_bg=False, img_side="right", validate_key=None, validate_button=None, text_color=BLACK, font=("calibri", 12), bg=(LIGHT_GREEN, DARK_GREEN), outline=(3, BLACK)):
        
        assert type in ["default", "img", "both"]
        self.type = type
        self.sound = sound
        
        if type == "img" or type == "both":
            if type == "img":
                self.shown_bg = shown_bg
            try:
                self.image, self.image_hover = img
            except TypeError:
                self.image = self.image_hover = img
            self.img = self.image
            if type == "both":
                assert img_side in ["left", "right"]
                self.img_side = img_side
        
        if type == "default" or type == "both":
            self.shown_bg = True
            self.font = font
            self.text = text
            self.color = text_color
        
        if self.shown_bg:
            self.background = bg
            self.couleur_arriere_plan = self.background[0]
            self.default_outline = self.outline = outline[0]
            self.default_outline_color = self.outline_color = outline[1]
        else:
            self.couleur_arriere_plan = None
            self.default_outline = self.outline = 0
            self.default_outline_color = self.outline_color = YELLOW
        
        self.set_size()
        Objet.__init__(self, info_widget, True, validate_key, validate_button)
    
    def set_size(self):
        if self.type in ["default", "both"]:
            self.text_rect = rect_text(self.text, self.font)
            if self.type == "default":
                wt, ht = self.text_rect.size
                self.taille_bouton = (wt+20, ht+20)
            else:
                wt, ht = self.text_rect.size
                w = wt + self.img.get_width() + 25
                h = max([ht+20, self.img.get_height()+20])
                self.taille_bouton = (w, h)
        else: #self.type == "img"
            if self.shown_bg:
                self.taille_bouton = (self.img.get_width()+20, self.img.get_height()+20)
            else:
                self.taille_bouton = self.img.get_size()
        self.rect = generer_rect(size=self.taille_bouton)
    
    """-----------------------------------------------------------------------------------------"""
    
    @property
    def text(self):
        return self.__text
    
    @text.setter
    def text(self, text):
        self.__text = str(text) if text is not None else ""
        try:
            self.set_size()
        except AttributeError:
            pass
    
    @property
    def font(self):
        return self.__font
    
    @font.setter
    def font(self, font):
        try:
            self.__font = fonts(*font)
        except TypeError:
            self.__font = font
        try:
            self.set_size()
        except AttributeError:
            pass
    
    @property
    def sound(self):
        return self.__sound
    
    @sound.setter
    def sound(self, sound):
        if sound in sons:
            self.__sound = sound
    
    @property
    def background(self):
        return self.__background, self.__background_hover
    
    @background.setter
    def background(self, bg):
        if len(bg) == 3:
            self.__background = self.__background_hover = bg
        elif len(bg) == 2 and all(len(color) == 3 for color in bg):
            self.__background, self.__background_hover = bg
        else:
            pass
    
    @property
    def bg(self):
        return self.background
    
    @bg.setter
    def bg(self, bg):
        self.background = bg
    
    """-----------------------------------------------------------------------------------------"""
    
    def afficher(self, **kwargs):
        if any(key in kwargs for key in ["size", "width", "w", "height", "h"]):
            self.rect = modifier_rect(self.rect, **kwargs)
        else:
            self.rect = modifier_rect(self.rect, size=self.taille_bouton, **kwargs)
        CADRE = dessiner_rectangle(fenetre, self.couleur_arriere_plan, self.rect, outline=self.outline, outline_color=self.outline_color)
        if self.type == "default":
            afficher_texte(fenetre, self.text, self.font, color=self.color, centerx=CADRE.centerx, centery=CADRE.centery)
        elif self.type == "img":
            if self.shown_bg:
                afficher_image(fenetre, self.img, center=CADRE.center)
            else:
                afficher_image(fenetre, self.img, self.rect)
        else:
            r = generer_rect(width=self.text_rect.width+self.img.get_width()+5, centerx=CADRE.centerx)
            if self.img_side == "right":
                afficher_texte(fenetre, self.text, self.font, color=self.color, left=r.left, centery=CADRE.centery+2)
                afficher_image(fenetre, self.img, right=r.right, centery=CADRE.centery)
            else:
                afficher_image(fenetre, self.img, left=r.left, centery=CADRE.centery)
                afficher_texte(fenetre, self.text, self.font, color=self.color, right=r.right, centery=CADRE.centery+2)
            
        return self.rect

class CaseACocher(Objet):
    
    def __init__(self, info_widget, size, sound="selection", img=None, color=(0, 0, 0), statut=False):
        self.rect = pygame.Rect(0, 0, size, size)
        self.sound = sound
        self.default_outline = self.outline = 2
        self.default_outline_color = self.outline_color = self.color = color
        self.img = img
        
        self.statut = statut
        Objet.__init__(self, info_widget)
        
    def afficher(self, **kwargs):
        self.rect = CADRE = dessiner_rectangle(fenetre, None, self.rect, outline=self.outline, outline_color=self.outline_color, **kwargs)
        if self.statut is True:
            if self.img is not None:
                afficher_image(fenetre, self.img, center=CADRE.center)
            else:
                x, y = CADRE.center
                w, h = CADRE.size
                pygame.draw.line(
                    fenetre, self.color,
                    (x - (0.7*w)//2, y + (0.7*h)//2),
                    (x + (0.7*w)//2, y - (0.7*h)//2),
                    width=2
                )
                pygame.draw.line(
                    fenetre, self.color,
                    (x - (0.7*w)//2, y - (0.7*h)//2),
                    (x + (0.7*w)//2, y + (0.7*h)//2),
                    width=2
                )
        
        return self.rect

class BarreEchelle(Objet):
    
    def __init__(self, info_widget, bornes, size, scale_color, outline, depart=None, show_value=False, side="right", font=None):
        self.min, self.max = bornes
        self.ecart = self.max - self.min
        self.rect = pygame.Rect((0, 0), size)
        if depart is not None:
            self.set(depart)
        else:
            self.pourcentage = 0
        
        self.scale_color = scale_color
        self.default_outline = self.outline = outline[0]
        self.default_outline_color = self.outline_color = outline[1]
        
        self.validated = False
        self.show_value = show_value
        assert side in ["left", "right"]
        self.side = side
        self.font = font
        Objet.__init__(self, info_widget)
    
    def set(self, value):
        assert value >= self.min and value <= self.max
        self.pourcentage = (value - self.min) / self.ecart
    
    def get(self):
        return self.value
        
    def afficher(self, **kwargs):
        self.rect = dessiner_barre_stats(fenetre, self.rect.size, self.pourcentage, color=self.scale_color, outline=self.outline, outline_color=self.outline_color, **kwargs)
        if self.show_value:
            if self.side == "left":
                afficher_texte(fenetre, int(self.value), self.font, centery=self.rect.centery, right=self.rect.left-10)
            elif self.side == "right":
                afficher_texte(fenetre, int(self.value), self.font, centery=self.rect.centery, left=self.rect.right+10)
        return self.rect
        
    def mouse_event(self, event):
        CADRE = self.rect
        if event.type == MOUSEMOTION and self.rect.collidepoint(event.pos):
            self.widget_manager.ligne = self.ligne
            self.widget_manager.colonne = self.colonne
        
        if event.type == MOUSEBUTTONDOWN and CADRE.collidepoint(event.pos):
            self.active = True
        
        if (event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN) and self.active:
            x, y = event.pos
            self.pourcentage = (x - CADRE.x)/CADRE.width
        
        if event.type == MOUSEBUTTONUP:
            self.active = False
    
    def keyboard_controller_event(self, event):
        if (event.type == KEYDOWN and event.key == K_KP_MINUS) \
        or (event.type == JOYAXISMOTION and event.axis == controller.AXIS_LEFT_X and event.value <= -0.8):
            self.value -= 2 if event.type == KEYDOWN else 4
        
        if (event.type == KEYDOWN and event.key == K_KP_PLUS) \
        or (event.type == JOYAXISMOTION and event.axis == controller.AXIS_LEFT_X and event.value >= 0.8):
            self.value += 2 if event.type == KEYDOWN else 4
    
    @property
    def pourcentage(self):
        return self.__pourcentage
    
    @pourcentage.setter
    def pourcentage(self, p):
        self.__pourcentage = p
        self.__pourcentage = 1 if self.__pourcentage > 1 else self.__pourcentage
        self.__pourcentage = 0 if self.__pourcentage < 0 else self.__pourcentage
        self.__value = self.min + (self.ecart * self.__pourcentage)
    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, v):
        self.__value = v
        self.__value = self.max if self.__value > self.max else self.__value
        self.__value = self.min if self.__value < self.min else self.__value
        self.__pourcentage = (self.__value - self.min) / self.ecart