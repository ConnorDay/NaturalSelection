import math
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