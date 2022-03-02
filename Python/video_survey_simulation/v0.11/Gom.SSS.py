#
# GOM Small Scale Simulation
# Xuetao Lu
# 
# Released under the GNU General Public License

VERSION = "0.1"
import sys
import os
import fish
import camera
import pygame
import numpy as np
import random
import math
from pygame.locals import *


# Create camera
def cameraFactory(cameraGroup,surf,camera_pos):

    # Bait radius
    br = 50
    # Camera radius
    cr = 10
    camera.Camera(camera_pos, cr, camera.Bait(br, 0.05), cameraGroup)
    # Draw camera territory
    pygame.draw.circle(surf, ((255, 0, 0)), ((int(camera_pos[0]), int(camera_pos[1]))), cr, 1)
    pygame.draw.circle(surf, ((255, 0, 0)), ((int(camera_pos[0]), int(camera_pos[1]))), br, 1)

# Create fishes
def fishFactory(home,sigma,radius,fishGroup,surf,n_fish,cameraGroup):
    # Initialise parameters
    for i in xrange(0,n_fish):
        x = int(np.random.multivariate_normal(home, sigma, 1)[0,0])
        y = int(np.random.multivariate_normal(home, sigma, 1)[0,1])
        fish.Fish(np.array([x,y]), home, sigma, radius, cameraGroup, fishGroup)

    # Draw fish territory
    pygame.draw.circle(surf, ((0, 255, 0)), ((home[0], home[1])), 5)
    pygame.draw.circle(surf, ((0, 255, 0)), ((home[0], home[1])), int(math.sqrt(sigma[0,0])), 1)
    pygame.draw.circle(surf, ((0, 255, 0)), ((home[0], home[1])), int(2*math.sqrt(sigma[0,0])), 1)


# Main function    
def main():

    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((900,500),pygame.RESIZABLE)
    pygame.display.set_caption('GOM Small Scale Simulation')

    # Fill background, here I need to load the map as the background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    # Create fishe & camera groups
    fish_group = pygame.sprite.Group()
    camera_group = pygame.sprite.Group()

    camera_pos = np.array([450,120])
    cameraFactory(camera_group,background,camera_pos)

    home1 = np.array([270,250])
    home2 = np.array([630,250])
    sigma = np.array([[10000,0],[0,10000]])
    radius = 25

    fishFactory(home1,sigma,radius,fish_group,background,2,camera_group)
    fishFactory(home2,sigma,radius,fish_group,background,1,camera_group)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialise clock
    clock = pygame.time.Clock()

    # Event loop
    while 1:
        # Make sure game doesn't run at more than 60 frames per second
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == QUIT:
                return

        #camera_group.clear(screen,background)

        #fish_group.clear(screen,background)
        fish_group.update()
        fish_group.draw(screen)
        camera_group.draw(screen)
        pygame.display.flip()

        #pygame.time.delay(50)

if __name__ == '__main__': main()
