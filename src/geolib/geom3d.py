'''
Created on Oct 6, 2013

@author: dewey
'''

from __future__ import division
from math import fabs, sqrt
from .geom2d import XY, Vector, Line, PointSeries, Triangle, Bounds

def almostEquals(val1, val2):
    '''Function to test equivalence of two float objects.'''
    delta = fabs(val2 - val1)
    deltaLimit = max((fabs(val1), fabs(val2))) * 1e-6 ;
    return delta <= deltaLimit

class XYZ(XY):
    '''Object to store a cartesian XY point.'''
    
    __slots__ = []
    
    def __new__(cls, x, y, z):
        return tuple.__new__(XY, (float(x), float(y), float(z)))
    
    def x(self):
        '''Returns the X Coordinate'''
        return self[0]
    def y(self):
        '''Returns the Y coordinate'''
        return self[1]
    
    def z(self):
        return self[2]
    
    @staticmethod
    def move(self, dx, dy, dz):
        '''Returns a new XY object moved by dx, dy, dz units.'''
        return XY(self[0]+dx, self[1]+dy, self[2]+dz)
    
    @staticmethod
    def positionVector(self):
        '''Returns a Vector object describing this position'''
        return Vector(self[0], self[1], self[2])
    
    @staticmethod
    def distanceTo(self, other):
        '''Calculates the cartesian distance to another XY object'''
        return sqrt((other[0]-self[0])**2 + (other[1]-self[1])**2 + (other[2]-other[2])**2)
    
    @staticmethod
    def approxEq(self, other):
        '''Returns true if this object is very close to another XY point, as determined by almostEquals()'''
        return almostEquals(self[0], other[0]) and almostEquals(self[1], other[1]) and almostEquals(self[2], other[2])
    
    @staticmethod
    def xy(self):
        return XY(self[0], self[1])
    
    @staticmethod
    def midpoint(self, other):
        tx = self[0] + other[0]
        ty = self[1] + other[1]
        tz = self[2] + other[2]
        return XY(tx/2.0, ty/2.0, tz/2.0)

    
class Line3D(Line):
    '''Represents a line from A to B, taking into account Z coordinates for length.'''
    
    def length(self):
        '''Returns the length of the line'''
        x1, y1, z1 = self.start()
        x2, y2, z2 = self.end()
        sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    
    def fraction(self, fraction):
        '''Returns the point at fraction length along the line (e.g. fraction(0.5) gives the midpoint of the line)'''
        x1, y1, z1 = self.__start
        x2, y2, z2 = self.__end
        xDiff = (x2-x1)*fraction
        yDiff = (y2-y1)*fraction
        zDiff = (z2-z1)
        return XY(x1+xDiff, y1+yDiff, z1+zDiff)
    
    def midpoint(self):
        return XYZ.midpoint(self.start(), self.end())

class PointSeries3D(PointSeries):
    """A 2-dimensional, mutable series of points."""
    
    def __init__(self, points=[]):
        '''Constructs a 2-dimensional PointSeries using an iterable of points.'''
        self.__points = []
        for pt in points:
            self.__points.append(pt)
    
    def clear(self):
        self.__points = []
    
    def length(self):
        try:
            cumSum = 0
            for index in range(1, len(self)):
                pt1 = self[index-1]
                pt2 = self[index]
                cumSum += XYZ.distanceTo(pt1, pt2)
            return cumSum
        except IndexError:
            return None
    
    def append(self, point):
        self.__points.append(point)
        
    def insert(self, index, point):
        self.__points.insert(index, point)
    
    def removeIndex(self, index):
        del self.__points[index]
    
    def point(self, index):
        return self[index]
    
    def count(self):
        return len(self.__points)
    
    def __repr__(self):
        return "PointSeries(%s)" % `self.__points`
    
    def __setitem__(self, index, value):
        return self.__points.__setitem__(index, value)
    def __getitem__(self, index):
        return self.__points.__getitem__(index)
    def __len__(self):
        return self.__points.__len__()
    def __iter__(self):
        return self.__points.__iter__()

    
class Plane(object):
    '''Represents a plane passing through 3 points in the form Ax + By + Cz + D = 0'''

    def __init__(self, p1, p2, p3):
        
        self.points = (p1, p2, p3)
        self.triangle = Triangle(p1, p2, p3)
        self.bounds = Bounds.fromPoints(p1, p2, p3)
        
        v1 = Vector.fromPoints(p1, p2)
        v2 = Vector.fromPoints(p1, p3)
        normal = Vector.cross(v1, v2)
        
        self.__a = normal.i()
        self.__b = normal.j()
        self.__c = normal.k()
        self.__d = (self.__a * p1[0] + self.__b * p1[1] + self.__c*p1[2])
        
        self.__normal = normal
        
    def a(self):
        return self.__a
    def b(self):
        return self.__b
    def c(self):
        return self.__c
    def d(self):
        return self.__d
    
    def extrapolate(self, point):
        '''Returns the Z coordinate at the XY coordinates of point on this plane, or none if it is a vertical plane'''
        a, b, c = self.__normal
        d = self.__d
        if self.c() != 0:
            return (d - a * point[0] - b*point[1]) / c
    def interpolate(self, point):
        '''Returns the value of extrapolate(point) if the point is within the 2d triangle formed by p1, p2, and p3'''
        if self.triangle.contains(point):
            return self.extrapolate(point)
    
def xyzip(xyPoints, zValues):
    outList = []
    for index in xrange(min(len(xyPoints), len(zValues))):
        x, y = xyPoints[index]
        outList.append(XYZ(x, y, zValues[index]))
    return outList
    