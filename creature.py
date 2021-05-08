import math
import random
import pygame
import numpy
from thing import thing, corpse
from bodypart import *


class creature(thing):
    raceCount = 1
    highlight = None
    def __init__(self, world, x=0, y=0, parent = None, timer = 0, mutate = True):
        super().__init__(world,x,y)
        self.energy = 1.0
        self.hp = 1.0
        self.target = None
        self.color = (255,255,255)
        self.nest = False
        self.timer = timer
        self.fleeing = None
        self.attacking = False
        self.donating = False
        self.priorities = [
            self.startNesting,
            self.startHealing,
            self.startDonating,
            self.startEating,
            self.startMaddened,
            self.startHunting,
            self.startFleeing
        ]
        random.shuffle(self.priorities)
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
                for _ in range(int(math.ceil(parent.atr['mut']/roll))):
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
                            self.atr[atribute] = max(0.001,self.atr[atribute])
                            if atribute != 'stom':
                                self.atr[atribute] = min(1, self.atr[atribute])
                            #print("A " + atribute + " atribute has changed by: " + str(delta) + " for race " + str(self.race))
                self.world.addRace(self)
            self.world.event(f'A new creature of race ({self.race}) was born!')
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
            self.world.addRace(self)
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
    def getHunger(self):
        return self.energy / self.atr['stom']
    def getHp(self, trait):
        return numpy.prod([i.hp for i in self.parts[trait]])
    def getHealth(self):
        totalHP = sum([self.getHp(i) for i in self.parts.keys()]) + self.hp
        parts = len(self.parts.keys()) + 1
        return totalHP/parts
    def moveTo(self, obj):
        speed = self.getTrait('spd')
        if self.donating: #If the creature is donating it gets a speed boost
            speed *= 1.1
        
        reached = self.distance(obj) - obj.size - self.size < speed
        if reached:
            speed = self.distance(obj) - obj.size - self.size
        
        vY = obj.y - self.y
        vX = obj.x - self.x
        if vX == 0:
            self.y += speed * numpy.sign(vY)
            return reached
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
    def spawn(self):
        self.world.add_thing(creature(self.world,self.x,self.y,self, 60))
    
    def startNesting(self, food, others):
        if self.getHunger() <= 1: #The creature is not full
            return False
        if not self.nest: #The creature is not nesting
            return False
        if not self.target: #If a target has not already been defined, define one
            sight = self.getTrait('per')
            deltaX = random.randint(int(-sight),int(sight))
            deltaY = random.randint(int(-sight), int(sight))
            self.target = thing(self.world,max(1, self.x + deltaX), max(1,self.y + deltaY))

            self.color = (255,20,147)
        
        return True

    def startHealing(self, food, others):
        if self.getHunger() <= 1: #The creature is not full
            return False
        if self.getHealth() == 1: #The creature does not need to heal
            return False
        
        self.target = self
        self.color = (100, 140, 17)

        return True
    
    def startDonating(self, food, others):
        if self.getHunger() <= 1: #The creature is not full
            return False
        if not others: #There are no other creatures around
            return False

        inNeed = []
        for c in others:
            if c.race != self.race: #if $c is not the same race as $self
                continue
            if c.getHunger() < self.atr['com']: #if $c is hungry enough
                inNeed.append(c)
            

        if not inNeed: #There are no members of the same race within range that are hungry
            return False

        self.target = self.closest(inNeed)
        self.donating = True
        
        self.color = (148, 0, 211)
        return True

    def startEating(self, food, others):
        if self.getHunger() > 1: #The creature is already full
            return False
        if not food: #If the food list is empty (ie there is no food)
            return False
        
        self.target = self.closest(food)
        self.color = (128, 128, 128)
        return True
    
    def startMaddened(self, food, others):
        if self.getHunger() > 1: #The creature is already full
            return False

        if food: #There is already nearby food
            return False
        if not others: #There is nothing to hunt
            return False
        
        if self.energy/self.atr['stom'] >= self.atr['agr']: #The creature is not hungry enough to be maddened
            return False
        
        self.target = self.closest(others)
        self.attacking = True
        self.color = (255, 0, 0)
        return True
    
    def startHunting(self, food, others):
        if self.getHunger() > 1: #The creature is already full
            return False
        if food: #There is already food nearby
            return False
        if not others: #There is nothing to hunt
            return False

        #Generate $small
        smallest = 10**100
        small = []
        for c in others:
            s = c.getMass()
            if s < smallest: #Reset $small if a new smallest is discovered
                smallest = s
                small = []
            if s == smallest: #Append creature to small
                small.append(c)
        
        #Generate $weak
        weak = []
        weakest = 1.0
        for c in small:
            h = c.getHealth()
            if h < weakest:
                weakest = h
                weak = []
            if h == weakest:
                weak.append(c)
        
        #Check to see if $self wants to fight anything in $weak
        sizeMult = smallest/self.getMass()
        strMult = len(weak[0].parts['str'])/len(self.parts['str'])
        healthMult = weakest / self.getHealth()
        if sizeMult * strMult * healthMult >= self.atr['agr']: #Any creature in $weak is too strong to be hunted
            return False

        self.target = self.closest(weak)
        self.color = ( 0, 0, 255 )
        return True

    def startFleeing(self, food, others):
        if self.getHunger() > 1: #The creature is already full
            return False
        if food: #There is already food nearby
            return False
        if not others: #There is nothing to hunt
            return False

        #Generate $big
        biggest = 0
        big = []
        for c in others:
            s = c.getMass()
            if s > biggest: #Reset $big if a new $biggest is discovered
                biggest = s
                big = []
            if s == biggest: #Append creature to small
                big.append(c)
        
        #Generate $big
        strong = []
        strongest = 0
        for c in big:
            h = c.getHealth()
            if h > strongest:
                strongest = h
                strong = []
            if h == strongest:
                strong.append(c)
        
        #Check to see if $self is scared of anything in $big
        sizeMult = biggest/self.getMass()
        strMult = len(strong[0].parts['str'])/len(self.parts['str'])
        healthMult = strongest / self.getHealth()
        if sizeMult * strMult * healthMult >= self.atr['fear']: #Any creature in $weak is too strong to be hunted
            return False
        
        close = self.closest(strong)
        if self.fleeing != close: #Assign a spot to flee to from the closest creature
            self.fleeing = close

            speed = self.getTrait('per')

            dy = close.y - self.y
            dx = close.x - self.x
            if dx == 0:
                self.target = thing(self.world, self.x, self.y - speed * numpy.sign(dy))
            else:
                degree = math.atan(abs(dy/dx))
                if dy < 0:
                    degree += math.pi
                    if dx > 0:
                        degree = math.pi - degree
                elif dx < 0:
                    degree = math.pi - degree
            
            degree += math.pi
            self.target = thing( self.world, math.cos(degree) * speed, math.sin(degree) * speed )

        self.color = (160, 82, 45)
        return True



        
    def getTarget(self):
        visible = [i for i in self.world.getVisible(self)]
        food = []
        others = []
        for i in visible:
            if i.isFood():
                food.append(i)
            elif i != self and type(i) == creature:
                others.append(i)        

        self.donating = False
        self.attacking = False
        for func in self.priorities: #Run through all the priorities for the creature and break when one finds and sets a target
            if func(food, others):
                break
        
        if not self.target: #the default case, if nothing else the creature will wander in a random direction
            self.target = thing(self.world)
            self.fleeing = None
            self.color = (255, 255, 255)
    
    def die(self):
        super().die()
        reason = "unknown"
        if self.energy <= 0:
            reason = "starvation"
        elif self.hp <= 0:
            reason = "murdered"
        
        self.world.event(f"A creature of race ({self.race}) has died! Reason: {reason}")
        self.world.add_thing(corpse(self.world,self.x,self.y,self.getMass()))
         
         
    def hit(self, amount):
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
                self.die()
    
    def heal(self):
        #get injured parts
        before = self.getHealth()
        injured = []
        for trait in self.parts.keys():
            for part in self.parts[trait]:
                if part.hp < 1:
                    injured.append(part)
        if self.hp < 1:
            injured.append(self)
        #randomly select one to heal
        amount = 0
        if len(injured) > 0:
            repair = random.choice(injured)
            amount = random.random() * .25 + .25
            repair.hp = min(repair.hp + amount, 1)
        
    def update(self):
        
        if self.timer>0: #The creature is being born and cannot do anything
            self.timer -= 1
            return
        
        self.energy -= self.getUpkeep()
        if self.energy <= 0 or self.hp <= 0:
            self.die()
            return        
        
        self.getTarget()
        if self.target == self:
            self.heal()
            self.target = None
        elif self.moveTo(self.target): 
            #if the target has been reached
            if self.target.isFood():
                self.energy += self.target.eat()
                #check if the creature should try to nest
                if random.random() < self.getHunger()-1:
                    otherCreatures = 0
                    for other in self.world.getVisible(self):
                        if type(other) == creature and other != self:
                            otherCreatures += 1
                    #check if there are too many creatures around $self
                    if otherCreatures <= self.getTrait('per') / 50:
                        self.nest = True
            elif type(self.target) == creature:
                if self.donating: #Donate to the target
                    amount = (self.energy - self.atr['stom']) * self.atr['com']
                    self.energy -= amount
                    self.target.energy += amount
                    self.donating = False
                else: #Attack the target
                    strTotal = self.getTrait('str') + self.target.getTrait('str')
                    sizeAdv = self.target.getMass() / self.getMass()
                    strAdv = self.getTrait('str') / strTotal if strTotal > 0 else 0.0001
                    maxDamage = min(1, strAdv*sizeAdv)
                    dmg = random.uniform(0, maxDamage)
                    self.target.hit(dmg)
            else:
                if self.nest:
                    self.spawn()
                    self.energy -= .5
                    self.nest = False

            self.target = None


