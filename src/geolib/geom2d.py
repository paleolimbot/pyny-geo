'''
Created on Oct 6, 2013

@author: dewey
'''

from __future__ import division
from math import fabs, pi, sqrt, hypot

def almostEquals(val1, val2):
    '''Function to test equivalence of two float objects.'''
    delta = fabs(val2 - val1)
    deltaLimit = max((fabs(val1), fabs(val2))) * 1e-6 ;
    return delta <= deltaLimit

class XY(tuple):
    '''Object to store a cartesian XY point.'''
    
    __slots__ = []
    
    def __new__(cls, x, y):
        return tuple.__new__(XY, (float(x), float(y)))
    
    def x(self):
        '''Returns the X Coordinate'''
        return self[0]
    def y(self):
        '''Returns the Y coordinate'''
        return self[1]
    
    @staticmethod
    def move(self, dx, dy, dz=0):
        '''Returns a new XY object moved by dx, dy units.'''
        return XY(self[0]+dx, self[1]+dy)
    
    @staticmethod
    def positionVector(self):
        '''Returns a Vector object describing this position'''
        return Vector(self[0], self[1])
    
    @staticmethod
    def distanceTo(self, other):
        '''Calculates the cartesian distance to another XY object'''
        return hypot(other[0]-self[0], other[1]-self[1])
    
    @staticmethod
    def approxEq(self, other):
        '''Returns true if this object is very close to another XY point, as determined by almostEquals()'''
        return almostEquals(self[0], other[0]) and almostEquals(self[1], other[1])
    
    @staticmethod
    def midpoint(self, other):
        tx = self[0] + other[0]
        ty = self[1] + other[1]
        return XY(tx/2, ty/2)


class Vector(tuple):
    '''Represents a vector with components i, j, and k'''
    
    __slots__ = []
    
    def __new__(cls, i, j, k=0):
        return tuple.__new__(Vector, (i, j, k))
        
    def i(self):
        '''Returns the X component of the vector'''
        return self[0]
    def j(self):
        '''Returns the Y component of the vector'''
        return self[1]
    def k(self):
        '''Returns the Z component of the vector'''
        return self[2]
    
    @staticmethod
    def mag(self):
        '''Returns the magnitude of this vector'''
        return sqrt(self[0]**2 + self[1]**2 + self[2]**2)
    
    @staticmethod
    def point(self, point):
        '''Returns an XY or XYZ-like tuple assuming this vector is a displacement vector from point.
        will return the same number of dimensions as point.'''
        if len(point) == 2:
            return (point[0]+self[0], point[1]+self[1])
        elif len(point >= 3):
            return point[0]+self[0], point[1]+self[1], point[2]+self[2]
    
    @staticmethod
    def line(self, point):
        '''Returns a line starting at point and ending at the vector displacement from point'''
        return Line(point, self.point(point))
    
    @staticmethod
    def unit(self):
        '''Returns a unit vector version of this vector'''
        return self / self.mag()
    
    @staticmethod
    def cross(self, v2):
        '''Returns a Vector representing the cross product of this vector and another vector'''
        i = self[1]*v2[2] - self[2]*v2[1] ;
        j = self[2]*v2[0] - self[0]*v2[2] ;
        k = self[0]*v2[1] - self[1]*v2[0] ;
        return Vector(i, j, k)
    
    @staticmethod
    def dot(self, v2):
        '''Returns a float representing the dot product of this vector and another vector'''
        return self[0]*v2[0] + self[1]*v2[1] + self[2]*v2[2]
    
    @staticmethod
    def ortho(self):
        '''Of the infinite number of orthogonal vectors to this vector, returns one of them'''
        return Vector(-self[1], self[0], -self[2])
    
    @staticmethod
    def fromPoints(p1, p2):
        length = min(len(p1), len(p2))
        if length == 2:
            return Vector(p2[0]-p1[0], p2[1]-p1[1])
        elif length >= 3:
            return Vector(p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
        else:
            raise ValueError
    
    def __str__(self):
        return "%fi+%fj+%fk" % (self[0], self[1], self[2])
    
    def __repr__(self):
        if self[2] != 0:
            return "Vector(%f, %f, %f)" % (self[0], self[1], self[2])
        else:
            return "Vector(%f, %f)" % (self[0], self[1])
    
    def __nonzero__(self):
        return Vector.mag(self)
    
    def __eq__(self, other):
        return self[0]==other[0] and self[1]==other[1] and self[2]==other[2]
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __mul__(self, other):
        if(isinstance(other, Vector)):
            raise AttributeError
        return Vector(self[0] * other, self[1] * other, self[2] * other)
    
    def __rmul__(self, other):
        if(isinstance(other, Vector)):
            raise AttributeError
        return self.__mul__(other)
    
    def __neg__(self):
        return self.__mul__(-1)
    
    def __truediv__(self, other):
        if(isinstance(other, Vector)):
            raise AttributeError
        return Vector(self[0] / other, self[1] / other, self[2] / other)
    
    def __add__(self, other):
        if(not isinstance(other, Vector)):
            raise AttributeError
        return Vector(self[0]+other[0], self[1]+other[1], self[2]+other[2])
    
    def __sub__(self, other):
        if(not isinstance(other, Vector)):
            raise AttributeError
        return self.__add__(other.__neg__())
    
class Line(object):
    '''Represents a line from A to B'''
    __slots__ = ["__start", "__end"]
    
    def __init__(self, start, end):
        self.__start = start
        self.__end = end
    
    def start(self):
        '''Returns the start point of the line'''
        return self.__start
    def end(self):
        '''Returns the end point of the line'''
        return self.__end
    def length(self):
        '''Returns the length of the line'''
        p1 = self.__start
        p2 = self.__end
        x1 = p1[0]
        x2 = p2[0]
        y1 = p1[1]
        y2 = p2[1]
        return hypot(x2-x1, y2-y1)
    
    def fraction(self, fraction):
        '''Returns the point at fraction length along the line (e.g. fraction(0.5) gives the midpoint of the line)'''
        p1 = self.__start
        p2 = self.__end
        x1 = p1[0]
        x2 = p2[0]
        y1 = p1[1]
        y2 = p2[1]
        xDiff = (x2-x1)*fraction
        yDiff = (y2-y1)*fraction
        return XY(x1+xDiff, y1+yDiff)
    
    def midpoint(self):
        return XY.midpoint(self.__start, self.__end)
    
    def __eq__(self, other):
        if ((self.start() == other.start() and self.end() == other.end()) 
            or (self.start() == other.end() and self.end() == other.start())) :
            return True
        else:
            return False
        
    def __ne__(self, other):
        return not self.__eq__(other)

class Bounds(object):
    '''Represents maximum and minimum XY values that form a bounding rectangle'''
    
    __slots__ = ["__minx", "__maxx", "__miny", "__maxy"]
    
    def __init__(self, minx, maxx, miny, maxy):
        self.__minx = minx
        self.__maxx = maxx
        self.__miny = miny
        self.__maxy = maxy
    
    def topLeft(self):
        return XY(self.__minx, self.__maxy)
    def topRight(self):
        return XY(self.__maxx, self.__maxy)
    def bottomLeft(self):
        return XY(self.__minx, self.__miny)
    def bottomRight(self):
        return XY(self.__maxx, self.__miny)
    
    def width(self):
        return self.__maxx - self.__minx
    def height(self):
        return self.__maxy - self.__miny
    
    def centre(self):
        return XY.midpoint(self.topLeft(), self.bottomRight())
    
    def contains(self, point):
        '''Returns true if point is within or on the edge of these bounds'''
        return (point[0] >= self.__minx and point[0] <= self.__maxx and
                point[1] >= self.__miny and point[1] <= self.__maxy)
        
    
    def minx(self):
        return self.__minx
    def miny(self):
        return self.__miny
    def minz(self):
        return self.__minz
    def maxx(self):
        return self.__maxx
    def maxy(self):
        return self.__maxy
    def maxz(self):
        return self.__maxz
    
    def __add__(self, other):
        """Unites two bounds to form a bounds that encompasses both"""
        return Bounds.fromPoints(self.bottomLeft(), self.topRight(), other.bottomLeft(), other.topRight())
    
    def __eq__(self, other):
        return self.bottomLeft() == other.bottomLeft() and self.topRight() == other.topRight()
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return "Bounds(%f, %f, %f, %f)" % (self.__minx, self.__maxx, self.__miny, self.__maxy)
    
    def __str__(self):
        return `self`
    
    def rectangle(self):
        return Polygon((self.topLeft(), self.topRight(), self.bottomRight(), self.bottomLeft()))
    
    def subdivide(self, xCount, yCount):
        stepWidth = self.width() / xCount
        stepHeight = self.height() / yCount
        out = []
        for x in range(0, xCount):
            out.append([])
            for y in range(0, yCount):
                minx = self.__minx + x * stepWidth
                miny = self.__miny + y * stepHeight
                if x == xCount-1:
                    maxx = self.__maxx
                else:
                    maxx = minx + stepWidth
                if y == yCount-1:
                    maxy = self.__maxy
                else:
                    maxy = miny + stepHeight
                out[x].append(Bounds(minx, maxx, miny, maxy))
        return out
                    
    
    @staticmethod
    def fromPoints(*points):
        try:
            maxx = minx = points[0][0]
            maxy = miny = points[0][1]
            
            for pt in points:
                if pt[0] > maxx :
                    maxx = pt[0]
                if pt[1] > maxy :
                    maxy = pt[1]
                    
                if pt[0] < minx :
                    minx = pt[0]
                if pt[1] < miny :
                    miny = pt[1]

            return Bounds(minx, maxx, miny, maxy)
        except IndexError:
            raise ValueError, "not enough points to create bounds (at least 1)"

class Circle(object):
    '''Class representing a 2-dimensional circle'''

    __slots__ = ["__centre", "__radius"]

    def __init__(self, centre, radius):
        self.__centre = centre
        self.__radius = radius
    
    def radius(self):
        '''Returns the circle radius'''
        return self.__radius
    
    def centre(self):
        '''Returns the centre point'''
        return self.__centre
    
    def area(self):
        '''Returns the area of the circle'''
        return pi * self.__radius ** 2
    
    def perimeter(self):
        '''Returns the perimeter of the circle'''
        return self.__radius*2*pi
    
    def contains(self, point):
        '''Returns true if point is within or on the edge of this circle, false otherwise'''
        return XY.distanceTo(self.__centre, point) <= self.__radius
    
    def containsExclusive(self, point):
        '''Returns true if point is within this circle, false otherwise'''
        return XY.distanceTo(self.__centre, point) <= self.__radius
    
    def intersection(self, c2):
        '''Returns a list of points where this circle and c2 intersect, which may be empty.'''
        if(self != c2):
            betweenCentres = Line(self.centre(), c2.centre())
            d = betweenCentres.length()
            totalRadius = self.radius() + c2.radius()
            out = []
            
            if(d == totalRadius):
                fraction = self.radius() / totalRadius
                out.append(betweenCentres.fraction(fraction))
            elif d < totalRadius:
                try:
                    R = self.radius()
                    r = c2.radius()
                    a = sqrt((-d+r-R) * (-d-r+R) * (-d+r+R) * (d+r+R)) / d
                    yDist = a / 2
                    d1 = ( (d*d) - (r*r) + (R*R) ) / (2*d)
                    centreLens = betweenCentres.fraction(d1/d).positionVector()
                    yOffset = betweenCentres.ortho().unit() * yDist
                    out.append((centreLens+yOffset).point())
                    out.append((centreLens-yOffset).point())
                except ValueError:
                    pass
                
            return out
            
    def __repr__(self):
        return "Circle(%s, %s)" % (`self.__centre`, `self.__radius`)
    
    def __eq__(self, other):
        return self.__radius == other.__radius and self.__centre == other.__centre
    def __ne__(self, other):
        return not self.__eq__(other)

class PointSeries(object):
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
                cumSum += XY.distanceTo(pt1, pt2)
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
    
    def centre(self):
        return Bounds.fromPoints(*self).centre()
    
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

class Polygon(object):
    '''Represents a 2-dimensional n-gon'''
    
    def __init__(self, points):
        '''Constructs a Polygon using an iterable of points'''
        if len(points) < 3:
            raise ValueError
        self.__points = []
        for pt in points:
            self.__points.append(pt)
        self.__area = None
        self.__perimeter = None
    
    def points(self):
        return list(self.__points)
    
    def point(self, index):
        '''Returns the point at the given index'''
        return self[index]
    
    def line(self, index):
        '''Returns the line starting at the point at the given index and ending at index+1
        or index=0 if index is the last index'''
        if index==len(self)-1:
            return Line(self[-1], self[0])
        else:
            return Line(self[index], self[index+1])
        
    def count(self):
        '''Returns the number of points/sides in this polygon'''
        return len(self.__points)
    
    def perimeter(self):
        '''Returns the perimeter of this polygon'''
        if self.__perimeter is None:
            cumSum = 0
            for index in range(0, len(self)):
                pt1 = self[index]
                if len(self)-1 == index:
                    pt2 = self[0]
                else:
                    pt2 = self.point(index+1)
                cumSum += XY.distanceTo(pt1, pt2)
            self.__perimeter = cumSum
        return self.__perimeter
    
    def area(self):
        '''Returns the area of this polygon.'''
        if self.__area is None:
            cumSum = 0
            for index in range(0, len(self)):
                pt1 = self.point(index)
                if index == len(self)-1:
                    pt2 = self.point(0)
                else:
                    pt2 = self.point(index+1)
                toAdd = Vector.cross(XY.positionVector(pt1), XY.positionVector(pt2)).k()
                cumSum += toAdd
            self.__area = 0.5 * abs(cumSum)
        return self.__area
    
    def centre(self):
        return Bounds.fromPoints(*self).centre()
    
    def __repr__(self):
        return "Polygon(%s)" % `self.__points`
    
    def __getitem__(self, index):
        return self.__points.__getitem__(index)
    def __len__(self):
        return self.__points.__len__()
    def __iter__(self):
        return self.__points.__iter__()
    
class ComplexPolygon(Polygon):
    '''A polygon with an arbitrary number of interior "islands".'''
    def __init__(self, points, *interiorPolygons):
        super(ComplexPolygon, self).__init__(points)
        self.__interior = []
        for polygon in interiorPolygons:
            self.__interior.append(polygon)
        self.__area = None
    
    def interiorPolygons(self):
        return list(self.__interior)
    
    def area(self):
        if self.__area is None:
            outerArea = Polygon.area(self)
            for innerPolygon in self.__interior:
                outerArea -= Polygon.area(innerPolygon)
            self.__area = outerArea
        return self.__area
    
    def __repr__(self):
        return "ComplexPolygon(%s, *%s)" % (`self.points()`, `self.__interior`)

class Triangle(Polygon):
    
    def __init__(self, *points):
        if len(points) != 3:
            raise ValueError("Triangle must have three points")
        super(Triangle, self).__init__(points)
        self.__area = None
    
    def __len__(self):
        return super(Triangle, self).__len__()
    
    def a(self):
        '''Returns the first side of the triangle'''
        return self.line(0)
    def b(self):
        '''Returns the second side of the triangle'''
        return self.line(1)
    def c(self):
        '''Returns the third side of the triangle'''
        return self.line(2)
    
    def __repr__(self):
        return "Triangle(%s, %s, %s)" % (`self[0]`, `self[1]`, `self[2]`)
    
    def circumRadius(self):
        '''Returns the radius of the circle that circumscribes this triangle'''
        a = self.a().length()
        b = self.b().length()
        c = self.c().length()
        s = (a+b+c) / 2.0
        return (a * b * c) / (4 * sqrt(s * (a+b-s) * (a+c-s) * (b+c-s)))
    
    def circle(self):
        '''Returns the circle that passes through all three points of this triangle, or None if the circle does not exist'''
        if(self.area()):
            cr = Triangle.circumRadius(self)
            c1 = Circle(self[0], cr)
            c2 = Circle(self[1], cr)
            c3 = Circle(self[2], cr)
            solutions = c1.intersection(c2) + c2.intersection(c3)
            centre = Triangle.__dupxy(solutions)
            if centre is not None:
                return Circle(centre, cr)
    
    def contains(self, xy):
        '''Returns true if point is within or on the border of this triangle'''
        t1 = Triangle(self[0], self[1], xy)
        t2 = Triangle(self[1], self[2], xy)
        t3 = Triangle(self[2], self[0], xy)
        totalArea = t1.area() + t2.area() + t3.area()
        return almostEquals(totalArea, self.area()) and totalArea != 0
    
    @staticmethod
    def __dupxy(points):
        for i in xrange(len(points)):
            for j in xrange(i + 1, len(points)):
                if points[i].approxEq(points[j]):
                    return points[i]
    
    