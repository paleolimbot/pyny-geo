'''
Created on Oct 6, 2013

@author: dewey
'''

from geolib.geom2d import *
from geolib.geom3d import *

xy = XY(4.0001, 5.00492)
xy2 = XY(10., -1)
xy3 = (-1, 2)

line1 = Line(xy, xy2)
line2 = Line(xy2, xy3)
line3 = Line(xy3, xy)

print line1.length(), line2.length(), line3.length()


vect = Vector(*xy)
print vect, Vector.cross(vect, (2, 3, 6))

bounds = Bounds.fromPoints(xy, xy2, xy3)
print bounds, bounds.contains((5, 3))

circle = Circle((0,1), 5)
print circle, circle.containsExclusive(xy), circle.containsExclusive(xy2), circle.containsExclusive(xy3)

ps = PointSeries((xy, xy2, xy3))
ps.append((4,4))
print ps, ps.length(), ps.count(), len(ps)

ps = Polygon((xy, xy2, xy3))
print ps, ps.perimeter(), ps.area(), ps.count(), len(ps)

ps = Triangle(xy, xy2, xy3)
print ps, ps.perimeter(), ps.area(), ps.count(), len(ps)

xy = XYZ(4.0001, 5.00492, 6)
xy2 = XYZ(10, -1, 0)
xy3 = (-1, 2, 8.7)

line1 = Line3D(xy, xy2)
line2 = Line3D(xy2, xy3)
line3 = Line3D(xy3, xy)

print line1.length(), line2.length(), line3.length()


ps = PointSeries3D((xy, xy2, xy3))
ps.append((4,4,8))
print ps, ps.length(), ps.count(), len(ps)

plane = Plane(xy, xy2, xy3)

print plane, plane.bounds, plane.triangle, plane.extrapolate(xy), plane.extrapolate(XY.move(xy, -5, -3))

print ""

print XY(0,1) == XY(0.0, 1.0)