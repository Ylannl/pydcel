from math import hypot,sqrt

class vec2(object):
    """Basic 2D vector class"""
    def __init__(self, x, y):
        self.x, self.y = x, y
    
    def normalize(self):
        l = hypot(self.x,self.y)
        self.x = self.x/l
        self.y = self.y/l

    def normalized(self):
        l = hypot(self.x,self.y)
        v = vec2(self.x/l, self.y/l)
        return v
        
    def flip(self):
        self.x = -self.x
        self.y = -self.y
        
    def orthogonal_l(self):
        v = vec2(-self.y, self.x)
        v.normalize()
        return v
        
    def orthogonal_r(self):
        v = vec2(self.y, -self.x)
        v.normalize()
        return v

    def __add__(self, other):
        return vec2(self.x+other.x, self.y+other.y)
        
    def __sub__(self, other):
        return vec2(self.x-other.x, self.y-other.y)

    def __mul__(self, other):
        return vec2(self.x*other, self.y*other)
        
    def __repr__(self):
        return "vec({}, {})".format(self.x, self.y)