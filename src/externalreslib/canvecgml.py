'''
Created on Oct 30, 2013

@author: dewey
'''

import xml.sax
from xml.sax import ContentHandler
import zipfile
import tempfile

import nts
from geolib.geom2d import XY, PointSeries, ComplexPolygon

_DATA = "data"
_GEOMETRY = "geometry"

def geturl(ntsId):
    #TODO: finish url creation
    return "" % (ntsId[0], ntsId[1], ntsId[2])

def extractgml(zipped, directory):
    zipf = zipfile.ZipFile(zipped)
    for name in zipf.namelist():
        if name.endswith(".gml"):
            gmtemp = zipf.extract(name, directory)
            zipf.close()
            return gmtemp
    zipf.close()
    raise IOError, "no gml file found in archive"

class GMLHandler(ContentHandler):
    
    def __init__(self, targetLayerName):
        ContentHandler.__init__(self)
        self.targetLayerName = targetLayerName
        self.elements = []
        self.chars = u''
        self.currentdict 
    
    def startElementNS(self, name, qname, attrs):
        ContentHandler.startElementNS(self, name, qname, attrs)
        self.chars = u''
    
    def characters(self, content):
        self.chars += content
    
    def endElementNS(self, name, qname):
        ContentHandler.endElementNS(self, name, qname)
        self.chars = u''
    
    