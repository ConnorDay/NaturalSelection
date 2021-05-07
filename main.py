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

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

display = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
clock = pygame.time.Clock()

world = World(WINDOW_WIDTH, WINDOW_HEIGHT)
for _ in range(10):
    world.add_thing(creature(world))
for _ in range(10):
    world.add_thing(plant(world))

drawThread = threading.Thread(target=world.draw, args=(display,))
drawThread.start()

while world.running:
    world.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            world.running = False

world.running = False
world.event("Simulation Ended.")
drawThread.join()