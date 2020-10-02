import math
import pygame
import random
import numpy
import threading
from tkinter import *



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
    def draw(self):
        pass
    def update(self):
        pass

class bodypart():
    def __init__(self, atr, size=1.0, eff=0.5):
        self.hp = 1.0
        self.atr = atr
        self.size = size
        self.eff = eff
    def getEff(self):
        return 5.67887 * self.hp * self.size * math.log(self.eff+1, 10)
    def getCost(self):
        return (self.eff * (self.size ** 2)) / 1000
    def copy(self,bpart):
        b = bpart()
        b.size = self.size
        b.eff = self.eff
        return b
        
class eyestalk(bodypart):
    def __init__(self):
        super().__init__('per')
    def getEff(self):
        return super().getEff() * 100
    def copy(self):
        return super().copy(eyestalk)
class leg(bodypart):
    def __init__(self):
        super().__init__('spd')
    def getEff(self):
        return super().getEff()
    def copy(self):
        return super().copy(leg)
class arm(bodypart):
    def __init__(self):
        super().__init__('str')
    def getEff(self):
        return super().getEff()
    def copy(self):
        return super().copy(arm)
class corpse(thing):
    def __init__(self,x,y,size):
        super().__init__(x,y)
        self.size = (size*2)/3
        self.startSize = size
        self.timer = 300
    def isFood(self):
        return self.size > 0
    def draw(self):
        pygame.draw.circle(display, (255,255,0), (int(self.x),int(self.y)), int(self.size))
    def die(self):
        objects.remove(self)
        del self
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            if random.random() < self.size/(self.startSize):
                objects.append(plant(self.x,self.y,1))
            self.die()
    def eat(self):
        food = .25 if self.size >= 1 else .25*self.size
        self.size -= 1
        if self.size <= 0:
            self.die()
        return food

class creature(thing):
    raceCount = 1
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
                races[self.race] = creature(parent=self, mutate = False)
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
            races[self.race] = creature(parent=self, mutate = False)
    def draw(self):
        #if self.target:
            #pygame.draw.line(display, (255,0,0), (int(self.x),int(self.y)), (int(self.target.x), int(self.target.y)))
        c = self.color
        if highlight == self.race:
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
    def spawn(self):
        objects.append(creature(self.x,self.y,self, 60))
    
    def getTarget(self, reached = False, capped = False):
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
                                    
                            
        if not self.target or reached: #the default case, if nothing else the creature will wander in a random direction
            self.target = thing()
            self.fleeing = None
    
    def die(self):
        objects.append(corpse(self.x,self.y,self.getMass()))
        objects.remove(self)
        del self
         
         
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
        
    def update(self):
        
        if self.timer>0:
            self.timer -= 1
            return
        
        self.energy -= self.getUpkeep()
        if self.energy <= 0 or self.hp <= 0:
            self.die()
            return        
        
        self.getTarget()
        if self.target == self:
            self.heal()
            self.getTarget(True)
        elif self.moveTo(self.target): 
            self.color = (255,255,255)
            #if the target has been reached
            if self.target.isFood():
                self.energy += self.target.eat()
                if random.random() < self.energy-1:
                    self.nest = True
                    self.target = None
                    self.getTarget(capped=True)
                else:
                    self.getTarget()
            elif type(self.target) == creature:
                strTotal = self.getTrait('str') + self.target.getTrait('str')
                sizeAdv = self.target.getMass() / self.getMass()
                strAdv = self.getTrait('str') / strTotal if strTotal > 0 else 0
                maxDamage = min(1, strAdv*sizeAdv)
                dmg = random.uniform(0, maxDamage)
                self.target.hit(dmg)
            else:
                if self.nest:
                    self.spawn()
                    self.energy -= .5
                    self.nest = False
                self.getTarget(True)
        
class plant(thing):
    def __init__(self, x=0, y=0, fruits = 0):
        super().__init__(x,y)
        self.fruits = random.randint(4,8) if fruits == 0 else fruits
        self.size = self.fruits*2
    def draw(self):
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
        if self.fruits == 0:
            objects.remove(self)
            del self
        else:
            self.size -= 2
        
        return .5

display = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

objects = []
races = {}
prev = {}
alive = {}
update = True
highlight = None

def stopUpdate():
    global update
    update = False
    updateTk()
def startUpdate():
    global update
    global widgets
    update = True
    for w in widgets:
        w.destroy()
    widgets = [Button(main, text="Pause", command=stopUpdate)]
    widgets[0].grid()
def setColor(r):
    def func():
        global highlight
        highlight = r if highlight != r else None
    return func
    

main = Tk()
widgets = [Button(main, text="Pause", command=stopUpdate)]
widgets[0].grid()

def updateTk():
    rs = ""
    
    columns = 13
    
    counter = 1
    for w in widgets:
        w.destroy()
        
        
    frameCanvas = Frame(main)
    frameCanvas.grid(row=0, column=0, sticky='nw')
    frameCanvas.grid_rowconfigure(0, weight=1)
    frameCanvas.grid_columnconfigure(0, weight=1)
    widgets.append(frameCanvas)
    
    canvas = Canvas(frameCanvas)
    canvas.grid(row=0, column=0, sticky='news')
    widgets.append(canvas)
    
    vsb = Scrollbar(frameCanvas, orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    
    widgets.append(vsb)
    
    canvas.configure(yscrollcommand=vsb.set)
    
    root = Frame(canvas)
    widgets.append(root)
    
    
    widgets.append(Label(root, text="RACE"))
    widgets[-1].grid(row=0, column=0, sticky=E)
    widgets.append(Label(root, text="COUNT"))
    widgets[-1].grid(row=0, column=1, sticky=E)
    widgets.append(Label(root, text="ATRIBUTES"))
    widgets[-1].grid(row=0, column=2, columnspan=2, sticky=W)
    #widgets.append(Label(root, text="STR PARTS"))
    #widgets[-1].grid(row=0, column=4, columnspan=2, sticky=W)
    for race in alive.keys():
        
        #widgets.append(ttk.Separator(root, orient=HORIZONTAL))
        widgets.append(Frame(root, bg="black", height=1, relief=SUNKEN))
        widgets[-1].grid(row=counter, columnspan=columns, sticky='ew')
        counter += 1
        
        widgets.append(Button(root, text=race+": ", command=setColor(race)))
        widgets[-1].grid(row=counter, column=0, sticky='we')
        widgets.append(Label(root, text=str(alive[race])))
        widgets[-1].grid(row=counter, column=1, sticky=W)
        
        c = races[race]
        atrCount = 0
        for atr in sorted(c.atr.keys()):
            widgets.append(Label(root, text=atr+": "))
            widgets[-1].grid(row=counter+atrCount, column=2, sticky=W)
            widgets.append(Label(root, text=str(c.atr[atr])))
            widgets[-1].grid(row=counter+atrCount, column=3, sticky=W)
            atrCount += 1
        
        partCount = []
        partNum = 0
        for part in sorted(c.parts.keys()):
            partCount.append(1)
            p = 0
            widgets.append(Label(root, text=part.upper()+" PARTS"))
            widgets[-1].grid(row=0, column=4 + (3 * partNum), columnspan=3, sticky=W)
            widgets.append(Label(root, text="Total: "))
            widgets[-1].grid(row=counter, column=4 + (3 * partNum), sticky=W)
            widgets.append(Label(root, text=str(c.getTrait(part))))
            widgets[-1].grid(row=counter, column=5 + (3 * partNum), sticky=W, columnspan=2)
            for ar in c.parts[part]:
                widgets.append(Label(root, text="Part "+str(p+1)))
                widgets[-1].grid(row=counter+partCount[partNum], column=4 + (3 * partNum), sticky=W)
                widgets.append(Label(root, text="Eff: "))
                widgets[-1].grid(row=counter+partCount[partNum], column=5 + (3 * partNum), sticky=W)
                widgets.append(Label(root, text=str(c.parts[part][p].eff)))
                widgets[-1].grid(row=counter+partCount[partNum], column=6 + (3 * partNum), sticky=W)
                partCount[partNum] += 1
                
                widgets.append(Label(root, text="Size: "))
                widgets[-1].grid(row=counter+partCount[partNum], column=5 + (3 * partNum), sticky=W)
                widgets.append(Label(root, text=str(c.parts[part][p].size)))
                widgets[-1].grid(row=counter+partCount[partNum], column=6 + (3 * partNum), sticky=W)
                
                partCount[partNum] += 1
                p += 1
            
            partNum += 1
        
        partCount.append(atrCount)
        counter += 1 + max(partCount)
    
    widgets.append(Button(main, text="Resume", command=startUpdate))
    widgets[-1].grid(row=1,column = 0)
    #widgets.append(Scrollbar(root, orient="vertical", command = canvas.yview))
    canvas.create_window((0,0), window=root, anchor='nw')
    
    root.update_idletasks()
    
    bbox = canvas.bbox("all")
    w = bbox[2]-bbox[1]
    
    canvas.config(scrollregion = bbox, width=w, height=400)


running = True
for _ in range(10):
    objects.append(creature())
for _ in range(20):
    objects.append(plant())
while running:
    try:
        main.update()
    except:
        running = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    display.fill((0,0,0))
    spawn = True
    alive = {}
    for obj in objects:
        if obj in objects: #this line exists because an $obj can be removed from $objects during the for loop
            obj.draw()
            if update:
                obj.update()
                if type(obj) == creature:
                    if obj.race in alive.keys():
                        alive[obj.race] += 1
                    else:
                        alive[obj.race] = 1
                    
                    spawn = False
    
    prev = alive
    if spawn and update:
        print("All creatures died! Spawning more!")
        objects.append(creature(parent=random.choice(list(races.values()))))
        
    pygame.display.update()
    #clock.tick(60)

pygame.quit()
main.quit()