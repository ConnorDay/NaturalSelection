import math
import random
import pygame
import numpy
from thing import *
from bodypart import *


class creature(thing):
    raceCount = 1
    races = {}
    highlight = None
    def __init__(self, x=0, y=0, parent = None, timer = 0, mutate = True):
        super().__init__(x,y)
        self.energy = 1.0
        self.hp = 1.0
        self.target = None
        self.color = (255,255,255)
        self.nest = False
        self.timer = timer
        self.fleeing = None
        self.attacking = False
        self.donating = False
        if parent:
            self.race = parent.race
            self.size = parent.size
            self.parts = {}
            for key in parent.parts.keys():
                self.parts[key] = [i.copy() for i in parent.parts[key]]
            self.atr = {}
            for key in parent.atr.keys():
                self.atr[key] = parent.atr[key]
            roll = random.random()
            if roll < parent.atr['mut'] and mutate:
                #mutates
                self.race += "-"+str(creature.raceCount)
                creature.raceCount += 1
                canGrowLimb = True
                for i in range(int(math.ceil(parent.atr['mut']/roll))):
                    if canGrowLimb and random.random() < parent.atr['mut']:
                        #grows a new limb
                        part = random.choice(list(self.parts.keys()))
                        if part == 'spd':
                            self.parts['spd'].append(leg())
                        elif part == 'per':
                            self.parts['per'].append(eyestalk())
                        elif part == 'str':
                            self.parts['str'].append(arm())
                        else:
                            self.parts[part].append(bodypart(part))
                            print("creating basic body part")
                        
                        canGrowLimb = False
                        #print("Race: " + str(self.race) + " grew a " + part + " limb!")
                    else:
                        #modifies something already existing
                        delta = ((random.random() * 0.5) + 0.5) * ((parent.atr['mut'] - roll) * random.choice([-1,1]))
                        if random.random() < .5:
                            #modifies a part
                            part = random.choice(list(self.parts.keys()))
                            if random.random() < .3:
                                #modify size
                                c = random.choice(self.parts[part])
                                c.size += delta
                                c.size = c.size if c.size >= .1 else .1
                                #print("A " + part + " part changed size by: " + str(delta) + " for race " + str(self.race))
                            else:
                                #modify eff
                                c = random.choice(self.parts[part])
                                c.eff += delta
                                c.eff = c.eff if c.eff >= .05 else .05
                                #print("A " + part + " part changed eff by: " + str(delta) + " for race " + str(self.race))
                        else:
                            #modifies an atribute
                            atribute = random.choice(list(self.atr.keys()))
                            self.atr[atribute] += delta
                            self.atr[atribute] = max(0,self.atr[atribute])
                            if atribute != 'stom':
                                self.atr[atribute] = min(1, self.atr[atribute])
                            #print("A " + atribute + " atribute has changed by: " + str(delta) + " for race " + str(self.race))
                self.races[self.race] = creature(parent=self, mutate = False)
        else:
            self.race = str(creature.raceCount)
            creature.raceCount += 1
            self.size = 1.0
            self.parts = {
                'spd': [leg()],
                'per': [eyestalk()],
                'str': [arm()]
            }
            self.atr = {
                'agr': random.random(),
                'fear': random.random(),
                'com': random.random(),
                'stom': random.random()*2,
                'mut': .05
            }
            self.races[self.race] = creature(parent=self, mutate = False)
    def draw(self, display):
        #if self.target:
            #pygame.draw.line(display, (255,0,0), (int(self.x),int(self.y)), (int(self.target.x), int(self.target.y)))
        c = self.color
        if self.highlight == self.race:
            c = (138, 69, 19)
        pygame.draw.circle(display, c, (int(self.x),int(self.y)), int(self.getMass()))
            
        
        
    def getTrait(self, trait):
        return sum([i.getEff() for i in self.parts[trait]])
    def getCost(self, trait):
        return sum([i.getCost() for i in self.parts[trait]])
    def getUpkeep(self):
        return self.getCost('spd') + self.getCost('per') + self.getCost('str')
    def getSize(self, trait):
        return sum([i.size for i in self.parts[trait]])
    def getMass(self):
        return self.getSize('spd') + self.getSize('per') + self.getSize('str') + self.size
    
    def getHp(self, trait):
        return numpy.prod([i.hp for i in self.parts[trait]])
    def getHealth(self):
        totalHP = sum([self.getHp(i) for i in self.parts.keys()]) + self.hp
        parts = sum(len(self.parts[i]) for i in self.parts.keys()) + 1
        return totalHP/parts
    def moveTo(self, obj):
        speed = self.getTrait('spd')
        
        reached = self.distance(obj) - obj.size - self.size < speed
        if reached:
            speed = self.distance(obj) - obj.size - self.size
        
        vY = obj.y - self.y
        vX = obj.x - self.x
        if vX == 0:
            self.y += speed * numpy.sign(vY)
            return
        degree = math.atan(abs(vY/vX))
        if vY < 0:
            degree += math.pi
            if vX > 0:
                degree = math.pi-degree
        elif vX < 0:
            degree = math.pi-degree
        
        self.x += math.cos(degree) * speed
        self.y += math.sin(degree) * speed
        
        return reached
        
    def isVisible(self, obj):
        return self.distance(obj) - obj.size - self.size < self.getTrait('per')
    def spawn(self, objects):
        objects.append(creature(self.x,self.y,self, 60))
    
    def getTarget(self, objects, reached = False, capped = False):
        visible = [i for i in objects if self.isVisible(i)]
        food = []
        others = []
        for i in visible:
            if i.isFood():
                food.append(i)
            elif i != self:
                others.append(i)        
        
        if not self.target in objects and type(self.target) != thing: #remove targets that don't exist, unless they are a random destination
            self.target = None
        
        if self.energy > self.atr['stom']: #check if the creature has excess energy
            if self.nest:
                if not self.target:
                    sight = self.getTrait('per')
                    deltaX = random.randint(int(-sight),int(sight))
                    diff = math.sqrt(sight**2 - deltaX**2)
                    deltaY = random.randint(int(-diff), int(diff))
                    self.target = thing(self.x + deltaX, self.y + deltaY)
            elif self.getHealth() < 1:
                self.target = self
        else:
            
            if food: #if food is availible, go to the closest source
                close = self.closest(food)
                if self.target != close:
                    self.target = close
            else: #if no food is availible
                if others:
                    if self.energy/self.atr['stom'] < self.atr['agr']: #The creature is maddened by hunger and attacks the closest creature
                        close = self.closest(others)
                        self.attacking = True
                        if self.target != close:
                            self.target = close
                    else: #The creature will examine the other creatures for weaknesses
                        smallest = 10**10
                        weakest = 1.0
                        small = []
                        biggest = 0
                        healthiest = 0
                        big = []
                        kin = []
                        for c in others:
                            h = c.getHealth()
                            #generate $small
                            if c.size < smallest:
                                smallest = c.size
                                small = []
                            if c.size == smallest:
                                if h < weakest:
                                    small = []
                                    weakest = h
                                small.append(c)
                            
                            #generate $big
                            if c.size > biggest:
                                biggest = c.size
                                big = []
                            if c.size == biggest:
                                if h > healthiest:
                                    big = []
                                    healthiest = h
                                big.append(c)
                            
                            #generate $kin
                            if c.race == self.race:
                                kin.append(c)
                                
                        close = self.closest(small) #find the closest of the wounded small creatures
                        sizeMult = smallest/self.size
                        strMult = len(close.parts['str'])/len(self.parts['str'])
                        healthMult = weakest / self.getHealth()
                        if sizeMult * strMult * healthMult < self.atr['agr']: #Stalk a weaker creature
                            if self.target != close:
                                self.target = close
                        else: #The creature will try to distance itself from stronger creatures
                            close = self.closest(big)
                            sizeMult = self.size/biggest
                            strMult = len(self.parts['str'])/len(close.parts['str'])
                            healthMult = self.getHealth() / healthiest
                            if sizeMult * strMult * healthMult < self.atr['fear']: #if a creature is scary to the creature
                                if self.fleeing != close:
                                    self.color = (0,0,255)
                                    close.color = (255,0,255)
                                    self.fleeing = close
                                    
                                    speed = self.getTrait('per')
                                    
                                    vY = close.y - self.y
                                    vX = close.x - self.x
                                    if vX == 0:
                                        self.target = thing(self.x, self.y - speed*numpy.sign(vY))
                                    else:
                                        degree = math.atan(abs(vY/vX))
                                        if vY < 0:
                                            degree += math.pi
                                            if vX > 0:
                                                degree = math.pi-degree
                                        elif vX < 0:
                                            degree = math.pi-degree
                                        
                                        degree += math.pi
                                        
                                        self.target = thing(math.cos(degree) * speed, math.sin(degree) * speed)
                            else: #the creature will attempt to donate food
                                close = self.closest(kin)
                                if close:
                                    otherHung = close.energy/close.atr['stom']
                                    selfHung = self.energy/self.atr['stom']
                                    if otherHung/selfHung: #the creature will donate to $close
                                        if self.target != close:
                                            self.target = close
                                            self.donating = True
                                    
                            
        if not self.target or reached: #the default case, if nothing else the creature will wander in a random direction
            self.target = thing()
            self.fleeing = None
    
    def die(self, objects):
        objects.append(corpse(self.x,self.y,self.getMass()))
        objects.remove(self)
        del self
         
         
    def hit(self, amount, objects):
        roll = random.random()
        size = 0
        mass = self.getMass()
        for a in self.parts.keys():
            m = self.getSize(a)
            if roll < (size+m)/mass:
                #atr to be hit
                for p in self.parts[a]:
                    if roll < (size+p.size)/mass:
                        if p.hp > 0:
                            p.hp -= amount
                            if p.hp >= 0:
                                break
                            else:
                                amount = abs(p.hp)
                                p.hp = 0
                            size += p.size
                        
                    else:
                        size += p.size
                    
                break
            else:
                size += m
        else:
            self.hp -= amount
            if self.hp <= 0:
                self.die(objects)
    
    def heal(self):
        #get injured parts
        injured = []
        for trait in self.parts.keys():
            for part in self.parts[trait]:
                if part.hp < 1:
                    injured.append(part)
        if self.hp < 1:
            injured.append(self)
        #randomly select one to heal
        if len(injured) > 0:
            repair = random.choice(injured)
            amount = random.random() * .25 + .25
            repair.hp = min(repair.hp + amount, 1)
        
    def update(self, objects):
        
        if self.timer>0:
            self.timer -= 1
            return
        
        self.energy -= self.getUpkeep()
        if self.energy <= 0 or self.hp <= 0:
            self.die(objects)
            return        
        
        self.getTarget(objects)
        if self.target == self:
            self.heal()
            self.getTarget(objects, True)
        elif self.moveTo(self.target): 
            self.color = (255,255,255)
            #if the target has been reached
            if self.target.isFood():
                self.energy += self.target.eat(objects)
                if random.random() < self.energy-1:
                    self.nest = True
                    self.target = None
                    self.getTarget(objects, capped=True)
                else:
                    self.getTarget(objects)
            elif type(self.target) == creature:
                if self.donating:
                    amount = (self.energy - self.atr['stom']) * self.atr['com']
                    self.energy -= amount
                    self.target.energy += amount
                    self.donating = False
                else:
                    strTotal = self.getTrait('str') + self.target.getTrait('str')
                    sizeAdv = self.target.getMass() / self.getMass()
                    strAdv = self.getTrait('str') / strTotal if strTotal > 0 else 0
                    maxDamage = min(1, strAdv*sizeAdv)
                    dmg = random.uniform(0, maxDamage)
                    self.target.hit(dmg, objects)
            else:
                if self.nest:
                    self.spawn(objects)
                    self.energy -= .5
                    self.nest = False
                self.getTarget(objects, True)


