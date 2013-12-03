'''
Created on Sep 29, 2013

@author: dewey
'''

from geolib.geom2d import Bounds
import struct

BOUNDS = Bounds(-180, 180, -56, 60)

CONTINENTS = ("Africa", "Australia", "Eurasia", "Islands", "North_America", "South_America")
REGIONS = ("Region_01", "Region_02", "Region_03", "Region_04", "Region_05", "Region_06", "Region_07")

def tileByPosition(lon, lat):
    tileX = int(lon + 180)
    tileY = int(lat + 56)
    return tileX, tileY

def tileById(stringId):
    #N15W086
    hemNS = stringId[:1]
    degLat = int(stringId[1:3])
    if hemNS == "S":
        degLat *= -1
    hemEW = stringId[3:4]
    degLon = int(stringId[4:])
    if hemEW == "W":
        degLon *= -1
    return tileByPosition(degLon, degLat)

def tileBounds(tile):
    minLat = tile[1] - 56
    minLon = tile[0] - 180
    return Bounds(minLon, minLon+1, minLat, minLat+1)

def stringIdFromTile(tile):
    minLat = tile[1] - 56
    minLon = tile[0] - 180
    if minLat < 0:
        hemNS = "S"
        minLat *= -1
    else:
        hemNS = "N"
        
    if minLon < 0:
        hemEW = "W"
        minLon *= -1
    else:
        hemEW = "E"
    
    minLat = str(minLat)
    minLon = str(minLon)    
    while len(minLat) < 2:
        minLat = "0" + minLat
    while len(minLon) < 3:
        minLat = "0" + minLon
        
    return hemNS + minLat + hemEW + minLon
    
def urlSRTM3(continent, tile):
    return "http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/%s/%s.hgt.zip" % (continent, stringIdFromTile(tile))
    
def urlSRTM1(region, tile):
    return "http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/%s/%s.hgt.zip" % (region, stringIdFromTile(tile))
    
def readHGT(filename, width, pixelset):
    fileObj = open(filename)
    for pixelX in xrange(width):
        for pixelY in xrange(width):
            result = fileObj.read(2)
            if result is None:
                fileObj.close()
                return
            pixelset(pixelX, pixelY, struct.unpack('>h', result)[0])
    fileObj.close()

SRTM3 = 1
SRTM1 = 2

class SRTMRaster(object):
    
    NONE_VALUE = -32767
    
    def __init__(self, srtmType, tile):
        self.type = srtmType
        self.tile = tile
        self.bounds = tileBounds(tile)
        self.stringId = stringIdFromTile(tile)
        if srtmType == SRTM3:
            self.dimentions = 1200
        elif srtmType == SRTM1:
            self.dimentions = 3600
        else:
            raise ValueError, "no such SRTM type"
        self.values = {}
    
    
    def width(self):
        return self.dimentions
    
    def height(self):
        return self.dimentions
    
    def valueAtLocation(self, point):
        if self.bounds.contains(point):
            latDiff = point.y() - self.bounds.miny()
            lonDiff = point.x() - self.bounds.minx()
            if 0 <= latDiff < 1 and 0 <= lonDiff < 1:
                return self.value(int(lonDiff * self.width()), int(latDiff * self.height()))
            else:
                return None
        else:
            return None
    
    def setValue(self, x, y, value):
        
        if 0 <= x < self.width() and 0 <= y < self.height():
            self.values[(x, y)] = value
        #else ignore, for the extra pixel on the edge of
    
    def value(self, x, y):
        key = (x, y)
        if self.values.has_key(key):
            return self.values[key]
        else:
            return None
    
    def readFrom(self, filename):
        readHGT(filename, self.dimentions+1, lambda x, y, val: self.setValue(x-1, y-1, val))
    
    