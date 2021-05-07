import math
import pygame
import random
import numpy
import threading
#from tkinter import *
from thing import plant
#from bodypart import *
from creature import creature
from world import World
import time

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

display = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
clock = pygame.time.Clock()

def runSim():
    world = World(WINDOW_WIDTH, WINDOW_HEIGHT)
    f = open(str(int(time.time())), "w")
    world.file = f

    world.event("Simulation Started.")
    for _ in range(10):
        world.add_thing(creature(world))
    for _ in range(10):
        world.add_thing(plant(world))

    drawThread = threading.Thread(target=world.draw, args=(display,))
    drawThread.start()

    good = True
    while world.running:
        world.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                world.running = False
                good = False

    world.running = False
    world.event("Simulation Ended.")
    drawThread.join()

    f.close()
    return good

running = True
while running:
    creature.raceCount = 1
    running = runSim()