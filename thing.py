import random
import math
import pygame

class thing():
    def __init__(self,x=0,y=0):
        x = 1 if x < 0 else x
        x = 1280 if x > 1280 else x
        y = 1 if y < 0 else y
        y = 720 if y > 720 else y
        self.x = int(x) if x > 0 else random.randint(0,1280)
        self.y = int(y) if y > 0 else random.randint(0,720)
        self.size = 0
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
    def draw(self, display):
        pass
    def update(self, objects):
        pass

class corpse(thing):
    def __init__(self,x,y,size):
        super().__init__(x,y)
        self.size = (size*2)/3
        self.startSize = size
        self.timer = 300
    def isFood(self):
        return self.size > 0
    def draw(self, display):
        pygame.draw.circle(display, (255,255,0), (int(self.x),int(self.y)), int(self.size))
    def die(self, objects):
        objects.remove(self)
        del self
    def update(self, objects):
        self.timer -= 1
        if self.timer <= 0:
            if random.random() < self.size/(self.startSize):
                objects.append(plant(self.x,self.y,1))
            self.die(objects)
    def eat(self, objects):
        food = .25 if self.size >= 1 else .25*self.size
        self.size -= 1
        if self.size <= 0:
            self.die(objects)
        return food

class plant(thing):
    def __init__(self, x=0, y=0, fruits = 0):
        super().__init__(x,y)
        self.fruits = random.randint(4,8) if fruits == 0 else fruits
        self.size = self.fruits*2
    def draw(self, display):
        pygame.draw.circle(display, (0,255,0), (self.x,self.y), self.size)
    def update(self, objects):
        if random.random() < 0.01:
            self.fruits += 1
            self.size += 2
            if self.fruits > 8:
                self.fruits = 8
                self.size = 16
    def isFood(self):
        return self.fruits > 0
    def eat(self, objects):
        self.fruits -= 1
        if self.fruits == 0:
            objects.remove(self)
            del self
        else:
            self.size -= 2

        return .5