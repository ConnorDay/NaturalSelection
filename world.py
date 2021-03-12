from thing import thing
import pygame
import math
class World:
    subdivisions = 100
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.objects = [[[] for _ in range(w//self.subdivisions+1)] for _ in range(h//self.subdivisions+1)]
        self.alive = {}
        self.prev = {}
        self.paused = False
        self.running = True
    def add_thing( self, t : thing):
        self.objects[int(t.y//self.subdivisions)][int(t.x//self.subdivisions)].append(t)
    def draw(self, display):
        while self.running:
            display.fill((0,0,0))
            for row in self.objects:
                for col in row:
                    for obj in col:
                        if obj.alive:
                            obj.draw(display)
            pygame.display.update()
    def update(self):
        if self.paused:
            return
        toAdd = []
        for row in self.objects:
            for col in row:
                toRemove = []
                for obj in col:
                    if obj.alive:
                        prevW = obj.x // self.subdivisions
                        prevH = obj.y // self.subdivisions
                        obj.update()
                        if obj.x // self.subdivisions != prevW or obj.y // self.subdivisions != prevH:
                            toRemove.append(obj)
                            toAdd.append(obj)
                    else:
                        toRemove.append(obj)
                        continue
                for rem in toRemove:
                    col.remove(rem)
        for a in toAdd:
            self.add_thing(a)


    def getVisible(self, obj):
        per = max(1,obj.getTrait("per")) ** 2
        wPosition = obj.x//self.subdivisions
        hPosition = obj.y//self.subdivisions
        wChunk = int(math.ceil((self.h//self.subdivisions)/per))
        hChunk = int(math.ceil((self.w//self.subdivisions)/per))

        wStart = int(max(0, wPosition - wChunk))
        hStart = int(max(0, hPosition - hChunk))
        wEnd = int(min(self.w//self.subdivisions, wPosition+wChunk))
        hEnd = int(min(self.h//self.subdivisions, hPosition+hChunk))

        visible = []
        for w in range(wStart,wEnd):
            for h in range(hStart, hEnd):
                check = 0
                x2 = w**2
                y2 = h**2

                #top left
                check += 1 if (x2 + y2 < per) else 0
                check << 1

                #top right
                check += 1 if (x2 + y2 + wChunk < per) else 0
                check << 1

                #bottom left
                check += 1 if (x2 + y2 + hChunk < per) else 0
                check << 1

                #bottom right
                check += 1 if (x2 + y2 + wChunk + hChunk < per) else 0
                check << 1

                if check == 15:
                    visible += self.objects[h][w]
                elif check > 0:
                    visible += [i for i in self.objects[h][w] if obj.isVisible(i)]
        return visible