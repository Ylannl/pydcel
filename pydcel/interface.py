from Tkinter import *

try:
    from pyflann import FLANN
    import numpy as np
    WITH_FLANN = True
except ImportError:
    WITH_FLANN = False

import math
from vector import vec2

from interface_draw import draw
HELP = """
q - quit
h - print help message
p - print dcel

e - iterate through halfedges
v - iterate through vertices
f - iterate through faces
"""

class dcelVis(Tk):
    def __init__(self, dcel):
        Tk.__init__(self)
        self.sizex = 700
        self.sizey = 700
        self.window_diagonal = math.sqrt(self.sizex**2 + self.sizey**2)
        self.title("DCELvis")
        self.resizable(0,0)

        self.bind('q', self.exit)
        self.bind('h', self.print_help)
        self.bind('p', self.print_dcel)

        self.bind('e', self.iteratehedge)
        self.bind('v', self.iteratevertex)
        self.bind('f', self.iterateface)
        self.canvas = Canvas(self, bg="white", width=self.sizex, height=self.sizey)
        self.canvas.pack()

        if WITH_FLANN:
            self.bind("<ButtonRelease>", self.remove_closest)
            self.bind("<Motion>", self.report_closest)

        self.coordstext = self.canvas.create_text(self.sizex, self.sizey, anchor='se', text='')
        self.info_text = self.canvas.create_text(10, self.sizey, anchor='sw', text='')
        
        self.tx = 0
        self.ty = 0

        self.highlight_cache = []
        self.bgdcel_cache = []

        self.draw = draw(self)

        if WITH_FLANN:
            self.kdtree = FLANN()
        self.D = None
        self.bind_dcel(dcel)
        self.print_help(None)

    def t(self, x, y):
        """transform data coordinates to screen coordinates"""
        x = (x * self.scale) + self.tx
        y = self.sizey - ((y * self.scale) + self.ty)
        return (x,y)

    def t_(self, x, y):
        """transform screen coordinates to data coordinates"""
        x = (x - self.tx)/self.scale
        y = (self.sizey - y - self.ty)/self.scale
        return (x,y)

    def print_help(self, event):
        print HELP

    def print_dcel(self, event):
        print self.D

    def bind_dcel(self, dcel):
        minx = maxx = dcel.vertexList[0].x
        miny = maxy = dcel.vertexList[0].y
        for v in dcel.vertexList[1:]:
            if v.x < minx:
                minx = v.x
            if v.y < miny:
                miny = v.y
            if v.x > maxx:
                maxx = v.x
            if v.y > maxy:
                maxy = v.y

        d_x = maxx-minx
        d_y = maxy-miny
        c_x = minx + (d_x)/2
        c_y = miny + (d_y)/2

        if d_x > d_y:
            self.scale = (self.sizex*0.8) / d_x
        else:
            self.scale = (self.sizey*0.8) / d_y

        self.tx = self.sizex/2 - c_x*self.scale
        self.ty = self.sizey/2 - c_y*self.scale

        self.D = dcel

        self.draw_dcel()

    def draw_dcel(self):
        self.draw.deleteItems(self.bgdcel_cache)
        self.draw_dcel_faces()
        self.draw_dcel_hedges()
        self.draw_dcel_vertices()
        
        self.hedge_it = self.type_iterator('hedge')
        self.face_it = self.type_iterator('face')
        self.vertex_it = self.type_iterator('vertex')

    def getClosestVertex(self, screenx, screeny):
        vertices = [np.array([v.x,v.y]) for v in self.D.vertexList]
        self.kdtree.build_index(np.array(vertices), algorithm='linear')

        x,y = self.t_(screenx, screeny)
        q = np.array([x,y])
        v_i = self.kdtree.nn_index(q,1)[0][0]

        return self.D.vertexList[v_i]

    def remove_closest(self, event):
        v = self.getClosestVertex(event.x, event.y)
        self.D.remove_vertex( v )
        self.draw_dcel()

    def report_closest(self, event):
        s = str(self.getClosestVertex(event.x, event.y))
        self.canvas.itemconfig(self.info_text, text=s )

    def iteratehedge(self, event):
        try:
            self.hedge_it.next()
        except StopIteration:
            self.hedge_it = self.type_iterator('hedge')
            self.hedge_it.next()

    def iterateface(self, event):
        try:
            self.face_it.next()
        except StopIteration:
            self.face_it = self.type_iterator('face')
            self.face_it.next()

    def iteratevertex(self, event):
        try:
            self.vertex_it.next()
        except StopIteration:
            self.vertex_it = self.type_iterator('vertex')
            self.vertex_it.next()


    def type_iterator(self, q='hedge'):
        if q == 'hedge':
            for e in self.D.hedgeList:
                yield self.explain_hedge(e)
        elif q == 'face':
            for e in self.D.faceList:
                yield self.explain_face(e)
        elif q == 'vertex':
            for e in self.D.vertexList:
                yield self.explain_vertex(e)

    def explain_hedge(self, e):
        print e
        self.draw.deleteItems(self.highlight_cache)

        i1 = self.draw_dcel_face(e.incidentFace, fill='#ffc0bf', outline='')
        i4 = self.draw_dcel_vertex(e.origin, size=7, fill='red', outline='')
        i2 = self.draw_dcel_hedge(e.next, arrow=LAST, arrowshape=(7,6,2), width=2, fill='#1a740c')
        i3 = self.draw_dcel_hedge(e.previous, arrow=LAST, arrowshape=(7,6,2), width=2, fill='#0d4174')
        i5 = self.draw_dcel_hedge(e, arrow=LAST, arrowshape=(7,6,2), width=3, fill='red')
        i6 = self.draw_dcel_hedge(e.twin, arrow=LAST, arrowshape=(7,6,2), width=3, fill='orange')

        self.highlight_cache = [i1,i2,i3,i4,i5,i6]

    def explain_vertex(self, v):
        print v
        self.draw.deleteItems(self.highlight_cache)

        i1 = self.draw_dcel_vertex(v, size=7, fill='red', outline='')
        i2 = self.draw_dcel_hedge(v.incidentEdge, arrow=LAST, arrowshape=(7,6,2), width=2, fill='red')

        self.highlight_cache = [i1,i2]

    def explain_face(self, f):
        print f
        self.draw.deleteItems(self.highlight_cache)

        i1 = self.draw_dcel_face(f, fill='#ffc0bf', outline='')
        i2 = self.draw_dcel_hedge(f.outerComponent, arrow=LAST, arrowshape=(7,6,2), width=3, fill='red')

        self.highlight_cache = [i1,i2]

    def draw_dcel_vertices(self):
        for v in self.D.vertexList:
            self.bgdcel_cache.append(self.draw_dcel_vertex(v))

    def draw_dcel_vertex(self, v, **options):
        if options == {}:
            options = {'size':5, 'fill':'blue', 'outline':''}
        
        return self.draw.point(v.x, v.y, **options)

    def draw_dcel_hedges(self):
        for e in self.D.hedgeList:
            self.bgdcel_cache.append(self.draw_dcel_hedge(e))

    def draw_dcel_hedge(self, e, **options):
        if options == {}:
            options = {'arrow':LAST, 'arrowshape':(7,6,2), 'fill': '#444444'}

        offset = .02
        sx,sy = e.origin.x, e.origin.y
        ex,ey = e.twin.origin.x, e.twin.origin.y
        vx,vy = ex - sx, ey - sy
        v = vec2(vx, vy)
        v_ = v.orthogonal_l()*offset

        v = v - v.normalized()*.25
        ex, ey = sx+v.x, sy+v.y
        
        return self.draw.edge( (sx+v_.x, sy+v_.y), (ex+v_.x, ey+v_.y) , **options)

    def draw_dcel_faces(self):
        for f in self.D.faceList:
            self.bgdcel_cache.append(self.draw_dcel_face(f))

    def draw_dcel_face(self, f, **options):
        if f == self.D.infiniteFace:
            print 'Im not drawing infiniteFace'
            return

        if options == {}:
            options = {'fill':'#eeeeee', 'outline':''}
        
        vlist = [ (v.x, v.y) for v in f.loopOuterVertices() ]
        return self.draw.polygon(vlist, **options)

    def find_closest(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # print event.x, event.y
        # print x,y
        print self.canvas.find_closest(x, y)

    def exit(self, event):
        print "bye bye."
        self.quit()
        self.destroy()
