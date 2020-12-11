import math
import pygame
import random
import numpy
import threading
from tkinter import *
from thing import *
from bodypart import *
from creature import *


display = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

objects = []
prev = {}
alive = {}
update = True

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
        creature.highlight = r if creature.highlight != r else None
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
        
        c = creature.races[race]
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
            obj.draw(display)
            if update:
                obj.update(objects)
                if type(obj) == creature:
                    if obj.race in alive.keys():
                        alive[obj.race] += 1
                    else:
                        alive[obj.race] = 1
                    
                    spawn = False
    
    prev = alive
    if spawn and update:
        print("All creatures died! Spawning more!")
        objects.append(creature(parent=random.choice(list(creature.races.values()))))
        
    pygame.display.update()
    #clock.tick(60)

pygame.quit()
main.quit()