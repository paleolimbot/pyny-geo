'''
Created on Oct 5, 2013

@author: dewey
'''
from __future__ import division
from .proj import Projections, UniversalTransverseMercatorProjection

HEMISPHERE_N = UniversalTransverseMercatorProjection.HEMISPHERE_N
HEMISPHERE_S = UniversalTransverseMercatorProjection.HEMISPHERE_S

LAT_ZONES = "cdefghjklmnpqrstuwxx"

_ZONE_WIDTH = 6
_START_LON = -186.0
_ZONE_HEIGHT = 8
_START_LAT = -80.0
_END_LAT = 84

def lonZone(lon):
    return int((lon - _START_LON) / _ZONE_WIDTH)
    
def latZone(lat):
    try:
        index = int((lat - _START_LAT) / _ZONE_HEIGHT)
        return LAT_ZONES[index]
    except IndexError:
        return None

def hemisphere(lat):
    return HEMISPHERE_N if lat >= 0 else HEMISPHERE_S

def zone(point):
    return lonZone(point[0]), hemisphere(point[1])

def toUtm(latLonPoint, forceZone=None):
    if forceZone is None:
        forceZone = zone(latLonPoint)
    proj = Projections.utm(forceZone)
    return proj.project(latLonPoint), forceZone

def fromUtm(utmRef):
    zo = utmRef[1]
    proj = Projections.utm(zo)
    return proj.inverseProject(utmRef[0])

def __richtextCoordinate(coordinateS, tagA, tagB):
    dec = coordinateS.find(".")
    if dec == -1:
        dec = len(coordinateS)
    return coordinateS[:dec-5] + tagA + coordinateS[dec-5:dec-3] + tagB + coordinateS[dec-3:]

def formatUtm(utmRef, precision=0, rtTag=None):
    easting, northing = utmRef[0]
    elen = 6
    nlen = 7
    if precision > 0:
        elen += 1
        nlen += 1
    formE = "{:0%i.%if}" % (elen, precision)
    formN = "{:0%i.%if}" % (nlen, precision)
    
    if rtTag is None:
        form = formE +  "E " + formN + "N " + formatZone(utmRef[1])
        return form.format(easting, northing)
    else:
        strEasting = formE.format(easting)
        strNorthing = formN.format(northing)
        if len(rtTag.strip()):
            tagA = "<%s>" % rtTag
            tagB = "</%s>" % rtTag
        else:
            tagA = tagB = rtTag
        return "%sE %sN %s" % (__richtextCoordinate(strEasting, tagA, tagB), __richtextCoordinate(strNorthing, tagA, tagB), formatZone(utmRef[1]))
    
def formatZone(zo):
    return str(zo[0]) + zo[1]

def parseZone(zo):
    hem = zo[-1:]
    lonz = int(zo[:-1])
    return lonz, hem

def validZone(zo):
    return (zo[1] == HEMISPHERE_N or zo[1] == HEMISPHERE_S) and 0 <= zo[0] <= 60
        

