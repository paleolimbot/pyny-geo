from __future__ import division
from geom import *

class InterpolationError(Exception):
    pass

class tin(object):
    
    def __init__(self, points):
        if(len(points) < 3):
            raise ValueError("need three points or more to create tin")
        
        if(tin.__dupxy(points)):
            raise ValueError("no duplicate points allowed in TIN creation")
        
        self.__points = list(points)
        self.__edges = [] #2d lines
        self.__planes = [] #3d planes
    
    def create(self):
        #find shortest Line
        shortestLine = None
        firstPoints = None
        for i in xrange(len(self.__points)):
            for j in xrange(i + 1, len(self.__points)):
                l = Line(self.__points[i].xy(), self.__points[j].xy())
                if(shortestLine is not None):
                    if(l.length() < shortestLine.length()):
                        shortestLine = l
                        firstPoints = (self.__points[i], self.__points[j])
                else:
                    shortestLine = l
                    firstPoints = (self.__points[i], self.__points[j])
        #make initial Plane
        delpt = self.__getdelpt(shortestLine.start(), shortestLine.end(), None)
        self.__edges.append(shortestLine)
        if delpt is not None:
            firstPlane = Plane(firstPoints[0], firstPoints[1], delpt)
            self.__planes.append(firstPlane)
            self.__addedges(firstPlane, shortestLine)
        else:
            raise InterpolationError("could not find suitable third point in first iteration")
    
    def interpolate(self, point):
        for p in self.__planes:
            val = p.interpolate(point)
            if(val is not None):
                return val
                
    def __addedges(self, oldPlane, avoidedge):
        tri = oldPlane.Triangle
        for i in range(3):
            lineStartIndex = i
            lineEndIndex = i+1
            ptindex = i+2
            if ptindex > 2:
                ptindex -=3
            if lineEndIndex > 2:
                lineEndIndex -=3
            l = Line(tri[lineStartIndex], tri[lineEndIndex])
            pt = tri[ptindex]
            if(l != avoidedge and not l in self.__edges):
                self.__edges.append(l)
                point = self.__getdelpt(l.start(), l.end(), pt)
                if(point is not None):
                    newPlane = Plane(oldPlane.points[lineStartIndex], oldPlane.points[lineEndIndex], point)
                    self.__planes.append(newPlane)
                    self.__addedges(newPlane, l)
                    
    
    def __getdelpt(self, linepoint1, linepoint2, pointtoavoid):
        for pt in self.__points:
            if not tin.__samexy(linepoint1, pt) and not tin.__samexy(linepoint2, pt) and not tin.__samexy(pointtoavoid, pt):
                if(self.__isdeltri(Triangle((linepoint1, linepoint2, pt)))):
                    return pt
        
    
    def __isdeltri(self, tri):
        Circle = tri.Circle()
        if Circle is not None:
            for pt in self.__points:
                isTriPt = False
                for triPt in tri:
                    if(tin.__samexy(pt, triPt)):
                        isTriPt = True
                    
                if(Circle.containsInclusive(pt) and not isTriPt):
                    return False
            return True
        else:
            return False
    
    @staticmethod
    def __dupxy(points):
        for i in xrange(len(points)):
            for j in xrange(i + 1, len(points)):
                if tin.__samexy(points[i],points[j]):
                    return points[i]
                
    @staticmethod
    def __samexy(p1, p2):
        if p1 is None or p2 is None:
            return False
        return p1.x() == p2.x() and p1.y() == p2.y()
    

class datatable(object):
    
    def __init__(self):
        self.__main = {}
        self.__columns = []
        self.__points = []
    
    def put(self, loc, key, value):
        row = self.row(loc)
        self.addkey(key)
        row[key] = value
    
    def keys(self):
        return self.__columns[:]
    
    def putrow(self, loc, values):
        row = self.row(loc)
        for key,value in values:
            self.addkey(key)
            row[key] = value
    
    def addkey(self, key):
        if(not key in self.__columns):
            self.__columns.append(key)
    
    def row(self, loc):
        xy = loc.xy()
        if(not self.__main.has_key(xy)):
            self.__main[xy] = {}
            self.__points.append(xy)
        return self.__main[xy]
    
    
    
    
    