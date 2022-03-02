#Camera class and container

import os
import sys
import numpy as np
import pygame
import random
from pygame.locals import *

"""   
def load_png_camera(name):
    #Load image and return image object
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image, image.get_rect()
"""

class Bait(object):
    #docstring for bait
    def __init__(self, distance, lam):
        self.distance = distance
        self.lam = lam
    
    def set_lam(self,lmd):
        self.lam = lmd
    
    def bernoulli(self,dis):
        #probability decrease as distance increase by exponential distribution
        p = np.exp(-self.lam*dis)
        #draw under bernoulli(p)
        return np.random.binomial(1,p,1)

class Camera(pygame.sprite.Sprite):

    #Camera
    #Returns: Camera object
    #Functions: move, update_pos, update_home, update_sigma
    #Attributes: area, pos, home, sigma

    def __init__(self, pos, distance, bait, cameragroup):
        pygame.sprite.Sprite.__init__(self)
        #self.image, self.rect = load_png_camera('camerag.png')
        #screen = pygame.display.get_surface()
        #self.area = screen.get_rect()

        self.image=pygame.Surface((5,5))
        self.image.fill((255,0,0))
        self.rect=self.image.get_rect()
        self.rect.center=pos

        self.pos = pos
        self.distance = distance
        self.bait = bait
        self.count = 0
        self.add(cameragroup)

    def set_pos(self,p):
        self.pos = p
        self.rect = p

    def update(self):
        #count the number of catching fish
        self.count += 1
        #change the color of the camera to show catching
        random_color = random.randint(0,255),random.randint(0,255),random.randint(0,255)
        self.image.fill(random_color)
