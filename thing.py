import random
import math
import pygame

class thing():
    def __init__(self,world,x=0,y=0):
        x = 1280 if x > 1280 else x
        y = 720 if y > 720 else y
        self.x = int(x) if x > 0 else random.randint(1,1280)
        self.y = int(y) if y > 0 else random.randint(1,720)

        world.running
        self.world = world

        self.size = 0
        self.alive = True
    def isFood(self):
        return False
    def distance(self, other):
        return math.sqrt( (self.x - other.x)**2 + (self.y - other.y)**2 )
    def closest(self, others):
        closest = None
        dist = 10**10
        for obj in others:
            d = self.distance(obj)
            if d < dist:
                closest = obj
                dist = d
        return closest
    def die(self):
        self.alive = False
    def draw(self, display):
        pass
    def update(self, objects):
        pass

class corpse(thing):
    def __init__(self,world,x,y,size):
        super().__init__(world,x,y)
        self.size = (size*2)/3
        self.startSize = size
        self.timer = 300
    def isFood(self):
        return self.size > 0
    def draw(self, display):
        pygame.draw.circle(display, (255,255,0), (int(self.x),int(self.y)), max(1,int(self.size)))
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            if random.random() < self.size/(self.startSize):
                self.world.add_thing(plant(self.world,self.x,self.y,1))
            self.die()
    def eat(self):
        food = max(.25 if self.size >= 1 else .25*self.size, 0)
        self.size -= 1
        if self.size <= 0:
            self.die()
        return food

class plant(thing):
    def __init__(self, world, x=0, y=0, fruits = 0):
        super().__init__(world,x,y)
        self.fruits = random.randint(4,8) if fruits == 0 else fruits
        self.size = self.fruits*2
    def draw(self, display):
        pygame.draw.circle(display, (0,255,0), (self.x,self.y), self.size)
    def update(self):
        if random.random() < 0.01:
            self.fruits += 1
            self.size += 2
            if self.fruits > 8:
                self.fruits = 8
                self.size = 16
    def isFood(self):
        return self.fruits > 0
    def eat(self):
        self.fruits -= 1
        if self.fruits <= 0:
            self.die()
        else:
            self.size -= 2

        return .5