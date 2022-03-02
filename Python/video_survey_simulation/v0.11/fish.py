#Fish class and container

import os
import sys
import math
import hit_run as hr
import numpy as np
import random
import pygame
import copy
from pygame.locals import *


"""def load_png_fish(name):
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

class Fish(pygame.sprite.Sprite):

    #Fish
    #Functions: move, update_pos, update_home, update_sigma
    #Attributes: area, pos, home, sigma

    def __init__(self, pos, home, sigma,radius, cameraGroup, fishgroup):
        pygame.sprite.Sprite.__init__(self)
        #self.image, self.rect = load_png_fish('fish.png')
        #screen = pygame.display.get_surface()
        #self.area = screen.get_rect()

        self.image=pygame.Surface((5,5))
        random_color = random.randint(50,200),random.randint(50,200),random.randint(50,200)
        self.image.fill(random_color)
        self.rect=self.image.get_rect()
        self.rect.center=pos

        self.pos = pos
        self.angle = 0
        self.home = home
        self.sigma = sigma
        self.radius = radius
        self.cameraGroup = cameraGroup
        self.catched = 0
        self.add(fishgroup)

    def set_start_pos(self,p):
        self.pos = p
        self.rect = p

    def set_home(self,h):
        self.home = h

    def set_sigma(self,s):
        self.sigma = s

    def set_radius(self,r):
        self.radius = r

    def vnorm(self,v):
        return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

    def totuple(self,a):
        try:
            return tuple(self.totuple(i) for i in a)
        except TypeError:
            return a

    def update(self):
        pos,angle = hr.binorm_hitrun_circle(self.home,self.sigma,self.pos,self.angle,self.pos,self.radius,1)
        self.pos = pos
        self.angle = angle
        self.rect.center = self.totuple(pos)

        # calculate distance to check whether catched by camera, if catched update camera and ignore this fish
        for camera in self.cameraGroup.sprites():
            d = self.vnorm(pos - camera.pos)
            if d<=camera.bait.distance:
                if d<=camera.distance:
                    camera.update()
                    self.catched = 1
                    self.remove(self.groups())
                else:
                    drawbin = camera.bait.bernoulli(camera.bait.distance-camera.distance)
                    if drawbin:
                        camera.update()
                        self.catched = 1
                        self.remove(self.groups())
