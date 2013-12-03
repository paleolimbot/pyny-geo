'''
Created on Oct 2, 2013

@author: dewey
'''

from geolib.geom2d import XY
import geolib.proj as proj
from geolib.utm import *

CENT = 90

projList = (#proj.GoogleMapsProjection(CENT), 
            #proj.MercatorProjection(proj.Ellipsoids.WGS84, CENT),
            #proj.CylindricalEqualAreaProjection(proj.Ellipsoids.WGS84, CENT),
            proj.TransverseMercatorProjection(proj.Ellipsoids.WGS84, -3, 0.9996, 0, 500000),)

# 4987330
testPoints = [XY(-3, 45), XY(-3, -45), XY(-5, 45), XY(-3,0), XY(-7, 45)]


for point in testPoints:
    for proj in projList:
        xy = proj.project(point)
        latlon = proj.inverseProject(xy)
        print point, xy, latlon
        #print proj.latLonBounds()
        #print proj.projectedBounds()

if __name__ == "__main__":
    points = (XY(0,0), XY(-68.4, 45), XY(-72, -10))
    for point in points:
        utmRef = toUtm(point)
        latlon = fromUtm(utmRef)
        print point
        print utmRef, latlon
        print formatUtm(utmRef, 0), formatUtm(utmRef, 3), formatUtm(utmRef, 0), formatUtm(utmRef, 6)
        print latZone(point[1])
        print ""