'''
Created on Sep 24, 2013

@author: dewey
'''
from __future__ import division
import math
from proj import Projections, Ellipsoids
import units

def haversineDistance(origin, destination, ellipsoid=None, wraplat=True):
    
    lon1, lat1 = origin
    lon2, lat2 = destination

    dlatdeg = lat2-lat1
    dlondeg = lon2-lon1
    if wraplat:
        if dlondeg > 180:
            dlondeg = 360 - dlondeg
        elif dlondeg < -180:
            dlondeg = -360 - dlondeg
    
    radius = 6371008.7714
    if ellipsoid is not None:
        averageLat = (lat1+lat2) / 2
        radius = ellipsoid.radiusAt(averageLat)
    
    dlat = math.radians(dlatdeg)
    dlon = math.radians(dlondeg)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def equirectangularDistance(origin, destination, ellipsoid=None, wraplat=True):
    
    lon1, lat1 = origin
    lon2, lat2 = destination

    dlatdeg = lat2-lat1
    dlondeg = lon2-lon1
    if wraplat:
        if dlondeg > 180:
            dlondeg = 360 - dlondeg
        elif dlondeg < -180:
            dlondeg = -360 - dlondeg
        
    radius = 6371008.7714
    averageLat = (lat1+lat2) / 2
    if ellipsoid is not None: 
        radius = ellipsoid.radiusAt(averageLat)
    dlat = math.radians(dlatdeg)
    dlon = math.radians(dlondeg)
        
    x = dlon * math.cos(math.radians(averageLat))
    y = dlat    
    return math.sqrt(x*x + y*y) * radius
    
def sphericalCosinesDistance(origin, destination, ellipsoid=None, wraplat=True):
    lon1, lat1 = origin
    lon2, lat2 = destination
    
    dlondeg = lon2-lon1
    if wraplat:
        if dlondeg > 180:
            dlondeg = 360 - dlondeg
        elif dlondeg < -180:
            dlondeg = -360 - dlondeg
    
    radius = 6371008.7714
    if ellipsoid is not None:
        averageLat = (lat1+lat2) / 2
        radius = ellipsoid.radiusAt(averageLat)
            
    dlon = math.radians(dlondeg)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    
    return math.acos(math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2) * math.cos(dlon)) * radius;

def bearingTo(origin, destination):
    lon1, lat1 = origin
    lon2, lat2 = destination
    dlondeg = lon2-lon1
    if dlondeg > 180:
        dlondeg = 360 - dlondeg
    elif dlondeg < -180:
        dlondeg = -360 - dlondeg
        
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)    
    dlon = math.radians(dlondeg)
    
    y = math.sin(dlon) * math.cos(lat2);
    x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon);
    return math.degrees(math.atan2(y, x))
    
def distance(points, unit="m", wraplat=True, ellipsoid=Ellipsoids.WGS84, measureFunction=haversineDistance):
    if len(points) >= 2:
        distance = 0
        for index in range(1, len(points)):
            pt1 = points[index-1]
            pt2 = points[index]
            distance += measureFunction(pt1, pt2, ellipsoid, wraplat)
        return units.convertTo(distance, unit)
    else:
        raise ValueError, "too few points to measure distance"

def area(polygon, projection=None):
    firstPoint = polygon[0]
    if projection is None:
        projection = Projections.cylequalarea(firstPoint[0])
    projected = projection.projectPolygon(polygon)
    return projected.area()
    