'''
Created on Oct 2, 2013

@author: dewey
'''

import os
import zipfile
import tempfile
import re
import cStringIO
import xml.sax
from xml.sax import ContentHandler

from xmlutil import indent, opentag, closetag, writesimple
from geolib.geom2d import XY, PointSeries, Polygon, ComplexPolygon, Bounds

ATTR_ID = "id"

ATTR_NAME = "name"
ATTR_TYPE = "type"

TAG_COORDINATES = "coordinates"

TYPE_STRING = "string"
TYPE_FLOAT = "float"
TYPE_INTEGER = "int"
TYPE_DOUBLE = "double"
TYPE_BOOL = "bool"

RESOURCE_TAGS = ("href")

def _gencoords(*points):
    return " ".join(["%s,%s" % (point[0], point[1]) for point in points])

def _parsecoords(coordsString):
    series = PointSeries()
    for coordString in re.split(r"\s", coordsString.strip()):
        coords = coordString.split(",")
        series.append((float(coords[0]), float(coords[1])))
    return series

class KMLObject(object):
    
    def __init__(self, tagname, value=None):
        self.attrs = {}
        self.childtags = {}
        self.childobjs = []
        self.tag = tagname
        self.value = value
    
    def write(self, fileobj, ind):
        if self.value is not None:
            writesimple(fileobj, ind, self.tag, self.value, self.attrs)
        else:
            indent(fileobj, ind)
            opentag(fileobj, self.tag, self.attrs)
            for key, value in self.childtags.items():
                writesimple(fileobj, ind+1, key, value)
            self._writeContents(fileobj, ind+1)
            for childobj in self.childobjs:
                childobj.write(fileobj, ind+1)
            indent(fileobj, ind)
            closetag(fileobj, self.tag)
    
    def __str__(self):
        stringio = cStringIO.StringIO()
        self.write(stringio, 0)
        output = stringio.getvalue()
        stringio.close()
        return output
    
    def _writeContents(self, fileobj, ind):
        pass
    
    def _startParsing(self, attrs):
        pass
    
    def _handleStartTag(self, tagName, attrs):
        pass
    
    def _handleEndTag(self, tagName, contents):
        pass
    
    def _endParsing(self):
        pass

class KMLStyle(KMLObject):
    
    TAG_STYLE = "Style"
    
    def __init__(self):
        KMLObject.__init__(self, self.TAG_STYLE)
    
    def _handleStartTag(self, tagName, attrs):
        if (tagName == KMLSubStyle.TAG_LINESTYLE or 
            tagName == KMLSubStyle.TAG_POLYSTYLE or 
            tagName == KMLSubStyle.TAG_ICONSTYLE):
            return KMLSubStyle(tagName)
        
    def _handleEndTag(self, tagName, contents):
        if (tagName == KMLSubStyle.TAG_LINESTYLE or 
            tagName == KMLSubStyle.TAG_POLYSTYLE or 
            tagName == KMLSubStyle.TAG_ICONSTYLE):
            self.childobjs.append(contents)
    

class KMLSubStyle(KMLObject):
    
    TAG_LINESTYLE = "LineStyle"
    TAG_POLYSTYLE = "PolyStyle"
    TAG_ICONSTYLE = "IconStyle"

    TAG_COLOR = "color"
    TAG_FILL = "fill"
    TAG_OUTLINE = "outline"
    TAG_WIDTH = "width"
    
    TAG_ICON = "Icon"
    TAG_HREF = "href"
    TAG_HOTSPOT = "hotSpot"
    
    ATTR_X = "x"
    ATTR_Y = "y"
    ATTR_XUNITS = "xunits"
    ATTR_YUNITS = "yunits"
    
    UNIT_FRACTION = "fraction"
    UNIT_PIXELS = "pixels"
    UNIT_INSETPIXELS = "insetPixels"
    
    def __init__(self, tagname):
        KMLObject.__init__(self, tagname)
        
    def _handleStartTag(self, tagName, attrs):
        if tagName == self.TAG_HOTSPOT:
            attrsDict = {}
            for name in attrs.getNames():
                attrsDict[name] = attrs.getValue(name)
            hotspot = KMLObject(self.TAG_HOTSPOT, "")
            hotspot.attrs = attrsDict
            self.childobjs.append(hotspot)
            
        
    def _handleEndTag(self, tagName, innerText):
        if (tagName == self.TAG_COLOR or 
            tagName == self.TAG_FILL or 
            tagName == self.TAG_OUTLINE or 
            tagName == self.TAG_WIDTH):
            self.childtags[tagName] = innerText
        elif tagName == self.TAG_HREF:
            icsobj = KMLObject(self.TAG_ICON)
            icsobj.childtags[self.TAG_HREF] = innerText
            self.childobjs.append(icsobj)
            

class KMLSchema(KMLObject):
    TAG_SCHEMA = "Schema"
    TAG_SIMPLEFIELD = "SimpleField"
    
    def __init__(self, schemaId=None, types={}):
        KMLObject.__init__(self, self.TAG_SCHEMA)
        self.types = types
        self.schemaId = schemaId
    
    def setSchemaId(self, schemaId):
        self.schemaId = schemaId
        if schemaId:
            self.attrs[ATTR_ID] = schemaId
        else:
            del self.attrs[ATTR_ID]
    
    def syncData(self):
        self.childobjs = []
        for name, fieldtype in self.types.items():
            simplefield = KMLObject(self.TAG_SIMPLEFIELD, "")
            simplefield.attrs[ATTR_NAME] = name
            simplefield.attrs[ATTR_TYPE] = fieldtype
            self.childobjs.append(simplefield)
    
    def _startParsing(self, attrs):
        self.setSchemaId(attrs.getValue(ATTR_ID))
    
    def _handleStartTag(self, tagName, attrs):
        if tagName == self.TAG_SIMPLEFIELD:
            self.types[attrs.getValue(ATTR_NAME)] = attrs.getValue(ATTR_TYPE)
    
    def _endParsing(self):
        self.syncData()

class KMLExtendedData(KMLObject):
    
    TAG_EXTENDEDDATA = "ExtendedData"
    TAG_SCHEMADATA = "SchemaData"
    TAG_SIMPLEDATA = "SimpleData"
    TAG_DATA = "Data"
    TAG_VALUE = "value"
    ATTR_SCHEMAURL = "schemaUrl"
    
    schemas = {}
    
    def __init__(self, data=None):
        KMLObject.__init__(self, self.TAG_EXTENDEDDATA)
        if not data:
            data = {}
        self.data = data
        self.__currentName = None
        self.schema = None
        if self.data:
            self.syncData()
    
    def syncData(self):
        self.childobjs = []
        if self.schema:
            schemadata = KMLObject(self.TAG_SCHEMADATA)
            schemadata.attrs[self.ATTR_SCHEMAURL] = "#" + self.schema.schemaId
            for key, value in self.data.items():
                fullstring = `value`
                dataObj = KMLObject(self.TAG_SIMPLEDATA, fullstring)
                dataObj.attrs[ATTR_NAME] = key
                schemadata.childobjs.append(dataObj)
            self.childobjs.append(schemadata)
        else:
            for key, value in self.data.items():
                dataObj = KMLObject(self.TAG_DATA)
                dataObj.attrs[ATTR_NAME] = key
                dataObj.childtags[self.TAG_VALUE] = unicode(value)
                self.childobjs.append(dataObj)
    
    def _handleStartTag(self, tagName, attrs):
        if tagName == self.TAG_DATA:
            self.__currentName = attrs.getValue(ATTR_NAME)
        elif tagName == self.TAG_SCHEMADATA:
            schemaId = attrs.getValue(self.ATTR_SCHEMAURL)[1:]
            if schemaId in self.schemas:
                self.schema = self.schemas[schemaId]
        elif tagName == self.TAG_SIMPLEDATA:
            self.__currentName = attrs.getValue(ATTR_NAME)
                
    
    def _handleEndTag(self, tagName, innerText):
        if tagName == self.TAG_VALUE and self.__currentName:
            self.data[self.__currentName] = innerText
            self.__currentName = None
        elif tagName == self.TAG_SIMPLEDATA and self.__currentName:
            if self.schema and self.__currentName in self.schema.types:
                fieldtype = self.schema.types[self.__currentName]
                if fieldtype == TYPE_DOUBLE or fieldtype == TYPE_FLOAT:
                    value = float(innerText)
                elif fieldtype == TYPE_INTEGER:
                    value = int(innerText)
                else:
                    value = innerText
            else:
                value = innerText
            self.data[self.__currentName] = value
            self.__currentName = None
    
    def _endParsing(self):
        self.syncData()
        

class KMLFeature(KMLObject):
    
    TAG_PLACEMARK = "Placemark"
    TAG_FOLDER = "Folder"
    TAG_DOCUMENT = "Document"
    
    TAG_VISIBILITY = "visibility"
    TAG_NAME = "name"
    TAG_OPEN = "open"
    TAG_STYLEURL = "styleUrl"
    TAG_DESCRIPTION = "description"
    TAG_EXTENDEDDATA = "ExtendedData"    
    
    def __init__(self, tagname):
        KMLObject.__init__(self, tagname)
        self.extendedData = None
    
    def setExtendedData(self, extendedData):
        if self.extendedData in self.childobjs:
            self.childobjs.remove(self.extendedData)
        self.extendedData = extendedData
        self.childobjs.append(self.extendedData)

    
    def _handleStartTag(self, tagName, attrs):
        if tagName == self.TAG_EXTENDEDDATA:
            return KMLExtendedData()
        elif tagName == KMLSchema.TAG_SCHEMA:
            return KMLSchema()
        elif tagName == KMLStyle.TAG_STYLE:
            return KMLStyle()
    
    def _handleEndTag(self, tagName, contents):
        if tagName == self.TAG_EXTENDEDDATA:
            self.setExtendedData(contents)
        elif tagName == self.TAG_NAME:
            self.childtags[self.TAG_NAME] = contents
        elif tagName ==  self.TAG_DESCRIPTION:
            self.childtags[self.TAG_DESCRIPTION] = contents
        elif tagName == self.TAG_VISIBILITY:
            self.childtags[self.TAG_VISIBILITY] = contents
        elif tagName == self.TAG_OPEN:
            self.childtags[self.TAG_OPEN] = contents
        elif tagName == KMLSchema.TAG_SCHEMA:
            self.childobjs.append(contents)
        elif tagName == KMLStyle.TAG_STYLE:
            self.childobjs.append(contents)
        elif tagName == self.TAG_STYLEURL:
            self.childtags[self.TAG_STYLEURL] = contents

class KMLLatLonBox(KMLObject):
    
    TAG_LATLONBOX = "LatLonBox"
    TAG_NORTH = "north"
    TAG_SOUTH = "south"
    TAG_EAST = "east"
    TAG_WEST = "west"
    TAG_ROTATION = "rotation"
    
    def __init__(self):
        KMLObject.__init__(self, self.TAG_LATLONBOX)
        self.bounds = None
        self.rotation = 0
    
    def setBounds(self, bounds, rotation=0):
        self.childtags.clear()
        self.childtags[self.TAG_NORTH] = `bounds.maxy()`
        self.childtags[self.TAG_SOUTH] = `bounds.miny()`
        self.childtags[self.TAG_EAST] = `bounds.maxx()`
        self.childtags[self.TAG_WEST] = `bounds.minx()`
        self.bounds = bounds
        self.rotation = rotation
        if self.rotation != 0:
            self.childtags[self.TAG_ROTATION] = `rotation`
    
    def _handleEndTag(self, tagName, contents):
        if (tagName == self.TAG_NORTH or 
            tagName == self.TAG_SOUTH or 
            tagName == self.TAG_WEST or 
            tagName == self.TAG_EAST):
            self.childtags[tagName] = contents
        elif tagName == self.TAG_ROTATION:
            self.rotation = float(contents)
            if self.rotation != 0:
                self.childtags[tagName] = contents
            
    
    def _endParsing(self):
        self.bounds = Bounds(float(self.childtags[self.TAG_SOUTH]),
                             float(self.childtags[self.TAG_NORTH]),
                             float(self.childtags[self.TAG_WEST]),
                             float(self.childtags[self.TAG_EAST]))
        

class KMLGroundOverlay(KMLFeature):
    
    TAG_GROUNDOVERLAY = "GroundOverlay"
    TAG_COLOR = "color"
    TAG_HREF = "href"
    TAG_ICON = "Icon"
    
    def __init__(self, latlonbox=None, resource=None):
        KMLFeature.__init__(self, self.TAG_GROUNDOVERLAY)
        self.latlonbox = latlonbox
        self.resource = resource
    
    def setLatLonBox(self, latlonbox):
        for kmlobj in list(self.childobjs):
            if kmlobj.tag == KMLLatLonBox.TAG_LATLONBOX:
                self.childobjs.remove(kmlobj)
        self.latlonbox = latlonbox
        if latlonbox:
            self.childobjs.append(latlonbox)
    
    def setResource(self, resource):
        for kmlobj in list(self.childobjs):
            if kmlobj.tag == self.TAG_ICON:
                self.childobjs.remove(kmlobj)
        self.resource = resource
        if resource:
            icsobj = KMLObject(self.TAG_ICON)
            icsobj.childtags[self.TAG_HREF] = resource
            self.childobjs.append(icsobj)
    
    def _handleStartTag(self, tagName, attrs):
        if tagName == KMLLatLonBox.TAG_LATLONBOX:
            return KMLLatLonBox()
        else:
            return KMLFeature._handleStartTag(self, tagName, attrs)
    
    def _handleEndTag(self, tagName, contents):
        if tagName == self.TAG_HREF:
            self.setResource(contents)
        elif tagName == self.TAG_COLOR:
            self.childtags[self.TAG_COLOR] = contents
        elif tagName == KMLLatLonBox.TAG_LATLONBOX:
            self.setLatLonBox(contents)
        else:
            KMLFeature._handleEndTag(self, tagName, contents)
    
class KMLPlacemark(KMLFeature):
    
    def __init__(self):
        KMLFeature.__init__(self, self.TAG_PLACEMARK)
        self.geometry = None
    
    def setGeometry(self, kmlgeometry):
        for item in list(self.childobjs):
            if isinstance(item, KMLGeometry):
                self.childobjs.remove(item)
        self.geometry = kmlgeometry
        if kmlgeometry:
            self.childobjs.append(kmlgeometry)
        
    def _handleStartTag(self, tagName, attrs):
        if tagName == KMLGeometry.TAG_POINT:
            return KMLGeometry(KMLGeometry.TAG_POINT)
        elif tagName == KMLGeometry.TAG_LINESTRING:
            return KMLGeometry(KMLGeometry.TAG_LINESTRING)
        elif tagName == KMLGeometry.TAG_POLYGON:
            return KMLGeometry(KMLGeometry.TAG_POLYGON)
        else:
            return KMLFeature._handleStartTag(self, tagName, attrs)
    
    def _handleEndTag(self, tagName, contents):
        if tagName == KMLGeometry.TAG_POINT:
            self.setGeometry(contents)
        elif tagName == KMLGeometry.TAG_LINESTRING:
            self.setGeometry(contents)
        elif tagName == KMLGeometry.TAG_POLYGON:
            self.setGeometry(contents)
        else:
            KMLFeature._handleEndTag(self, tagName, contents)

class KMLContainer(KMLFeature):
    
    def __init__(self, tagname):
        KMLFeature.__init__(self, tagname)
    
    def _handleStartTag(self, tagName, attrs):
        if tagName == self.TAG_FOLDER:
            return KMLContainer(self.TAG_FOLDER)
        elif tagName == self.TAG_PLACEMARK:
            return KMLPlacemark()
        elif tagName == KMLGroundOverlay.TAG_GROUNDOVERLAY:
            return KMLGroundOverlay()
        else:
            return KMLFeature._handleStartTag(self, tagName, attrs)
    
    def _handleEndTag(self, tagName, contents):
        if tagName == self.TAG_FOLDER or tagName == self.TAG_PLACEMARK or tagName == KMLGroundOverlay.TAG_GROUNDOVERLAY:
            self.childobjs.append(contents)
        else:
            KMLFeature._handleEndTag(self, tagName, contents)


class KMLBoundary(KMLObject):
    TAG_INNERBOUNDARYIS = "innerBoundaryIs"
    TAG_OUTERBOUNDARYIS = "outerBoundaryIs"
    TAG_LINEARRING = "LinearRing"
    
    def __init__(self, tagname, series=None):
        KMLObject.__init__(self, tagname)
        self.pointseries = series
    
    def _writeContents(self, fileobj, ind):
        indent(fileobj, ind)
        opentag(fileobj, self.TAG_LINEARRING)
        pointseriesout = PointSeries(self.pointseries)
        pointseriesout.append(self.pointseries[0])
        writesimple(fileobj, ind+1, TAG_COORDINATES, _gencoords(*pointseriesout))
        indent(fileobj, ind)
        closetag(fileobj, self.TAG_LINEARRING)

    def _handleEndTag(self, tagName, innerText):
        if tagName == TAG_COORDINATES:
            self.pointseries = _parsecoords(innerText)
            if self.pointseries:
                self.pointseries.removeIndex(self.pointseries.count()-1)

class KMLGeometry(KMLObject):
    
    TAG_POINT = "Point"
    TAG_POLYGON = "Polygon"
    TAG_LINESTRING = "LineString"
    
    def __init__(self, tagname=None, geometryData=None):
        KMLObject.__init__(self, tagname)
        self.geometryData = geometryData
        if geometryData:
            self.setGeometryData(geometryData)
        self.__parseOuterRing = None
        self.__parseInnerRings = []
    
    def setGeometryData(self, item):
        self.geometryData = None
        self.childtags.clear()
        self.childobjs = []
        if isinstance(item, (XY, tuple)):
            self.geometryData = item
            self.tag = self.TAG_POINT
            self.childtags[TAG_COORDINATES] = _gencoords(item)
        elif isinstance(item, PointSeries):
            self.geometryData = item
            self.tag = self.TAG_LINESTRING
            self.childtags[TAG_COORDINATES] = _gencoords(*item)
        elif isinstance(item, Polygon):
            self.geometryData = item
            self.tag = self.TAG_POLYGON
            self.childobjs.append(KMLBoundary(KMLBoundary.TAG_OUTERBOUNDARYIS, item))
            if isinstance(item, ComplexPolygon):
                for innerpoly in item.interiorPolygons():
                    self.childobjs.append(KMLBoundary(KMLBoundary.TAG_INNERBOUNDARYIS, PointSeries(innerpoly)))
        else:
            raise ValueError, "invalid type provided as geometry data"
    
    def _handleStartTag(self, tagName, attrs):
        if tagName == KMLBoundary.TAG_OUTERBOUNDARYIS:
            return KMLBoundary(KMLBoundary.TAG_OUTERBOUNDARYIS)
        elif tagName == KMLBoundary.TAG_INNERBOUNDARYIS:
            return KMLBoundary(KMLBoundary.TAG_INNERBOUNDARYIS)
        
    def _handleEndTag(self, tagName, contents):
        if tagName == KMLBoundary.TAG_OUTERBOUNDARYIS:
            self.__parseOuterRing = contents.pointseries
            self.childobjs.append(contents)
        elif tagName == KMLBoundary.TAG_INNERBOUNDARYIS:
            self.__parseInnerRings.append(contents.pointseries)
            self.childobjs.append(contents)
        elif tagName == TAG_COORDINATES:
            series = _parsecoords(contents)
            if series.count() == 1:
                self.geometryData = series[0]
            elif series.count() > 1:
                self.geometryData = series
            self.childtags[TAG_COORDINATES] = _gencoords(*series)
    
    def _endParsing(self):
        if not self.geometryData:
            innerPolys = [Polygon(pointslist) for pointslist in self.__parseInnerRings]
            self.geometryData = ComplexPolygon(self.__parseOuterRing, *innerPolys)

class KMLDocument(object):
    
    HEADER = u'<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    
    def __init__(self, rootObject=None):
        self.rootObject = rootObject
        self.styles = {}
        self.schemas = {}
        self.resources = set()
        
    def write(self, fileobj):
        fileobj.write(self.HEADER)
        self.rootObject.write(fileobj, 1)
        fileobj.write(u"</kml>")
        fileobj.flush()
        
    def __str__(self):
        stringio = cStringIO.StringIO()
        self.write(stringio)
        output = stringio.getvalue()
        stringio.close()
        return output

class KMLObjectFactory(object):
    
    def __init__(self):
        pass
    
    @staticmethod
    def getobject(tagname):
        if tagname == KMLContainer.TAG_DOCUMENT:
            return KMLContainer(KMLContainer.TAG_DOCUMENT)
        elif tagname == KMLContainer.TAG_FOLDER:
            return KMLContainer(KMLContainer.TAG_FOLDER)
        elif tagname == KMLPlacemark.TAG_PLACEMARK:
            return KMLPlacemark()
        elif tagname == KMLGroundOverlay.TAG_GROUNDOVERLAY:
            return KMLGroundOverlay()
        else:
            return None

class KMLHandler(ContentHandler):
    
    def __init__(self):
            ContentHandler.__init__(self)
            self.chars = u""
            self.currentTag = None
            self.rootObject = None
            self.objectPath = []  
            self.styles = {}
            self.schemas = {}
            self.resources = set()
    
    def current(self):
        if self.objectPath:
            return self.objectPath[len(self.objectPath)-1]
        else:
            return None
    def startDocument(self):
        KMLExtendedData.schemas.clear()

    def startElement(self, name, attrs):
        self.chars = u""
        if not self.objectPath:
            obj = KMLObjectFactory.getobject(name)
            if obj:
                self.rootObject = obj
                self.objectPath.append(obj)
                obj._startParsing(attrs)
        else:
            current = self.current()
            if current:
                newObj = current._handleStartTag(name, attrs)
                if newObj:
                    newObj._startParsing(attrs)
                    self.objectPath.append(newObj)
            


    def endElement(self, currentName):
        if currentName in RESOURCE_TAGS:
            self.resources.add(self.chars)
            
        current = self.current()
        if current:
            if currentName == current.tag:
                current._endParsing()
                if current.tag == KMLSchema.TAG_SCHEMA:
                    KMLExtendedData.schemas[current.schemaId] = current
                    self.schemas[current.schemaId] = current
                elif current.tag == KMLStyle.TAG_STYLE and ATTR_ID in current.attrs:
                    self.styles[current.attrs[ATTR_ID]] = current
                self.objectPath.remove(current)
                newCurrent = self.current()
                if newCurrent:
                    newCurrent._handleEndTag(currentName, current)
            else:
                current._handleEndTag(currentName, self.chars)
        self.chars = u""

    def endDocument(self):
        KMLExtendedData.schemas.clear()

    def characters(self, content):
        self.chars += content
        
def parseKML(kmlfilename, resources=None):
    handle = open(kmlfilename)
    handler = KMLHandler()
    xml.sax.parse(handle, handler)
    document = KMLDocument(handler.rootObject)
    document.schemas = handler.schemas
    document.styles = handler.styles
    document.resources = handler.resources
    handle.close()
    
    if resources is not None and document.resources:
        parentdir = os.path.dirname(kmlfilename)
        for resource in document.resources:
            target = parentdir + os.path.sep + resource
            if os.path.isfile(target):
                resources[resource] = target
            else:
                resources[resource] = None
    
    return document

def parseKMZ(kmzfilename, resources=None):
    handle = zipfile.ZipFile(kmzfilename)
    ziplist = handle.namelist()
    for name in ziplist:
        if name.endswith(".kml"):
            tempdir = tempfile.mkdtemp()
            tempf = handle.extract(name, tempdir)
            output = parseKML(tempf)
            os.remove(tempf)
            
            zipresources = False
            if resources is not None and output.resources:
                for resource in output.resources:
                    if resource in ziplist:
                        zipresources = True
                        resources[resource] = handle.extract(resource, tempdir)
                    else:
                        resources[resource] = None
            
            if not zipresources:
                os.rmdir(tempdir)
            
            handle.close()
            return output
    else:
        handle.close()
        raise IOError, "no kml file found in kmz zip archive"

def writeKML(kmldoc, filename):                
    handle = open(filename, "w")
    kmldoc.write(handle)
    handle.close()

def writeKMZ(kmldoc, filename, resources={}):
    kmlname = "doc.kml"
    kmlfile = tempfile.mkstemp()[1]
    writeKML(kmldoc, kmlfile)
    kmzfile = zipfile.ZipFile(filename, "w")
    for relativePath, absolutePath in resources.items():
        kmzfile.write(absolutePath, relativePath)
    kmzfile.write(kmlfile, kmlname)
    kmzfile.close()

def parse(filename, resources=None):
    if zipfile.is_zipfile(filename):
        output = parseKMZ(filename, resources)
    else:
        output = parseKML(filename, resources)
    
    return output

def deleteresources(resources):
    #only use for KMZ temp directories!
    basedir = None
    success = True
    for value in resources.values():
        success = success and os.remove(value)
        basedir = os.path.dirname(value)
    if basedir:
        try:
            success = os.rmdir(basedir)
            return success and True
        except OSError:
            return False
    return success

if __name__ == "__main__":
    res = {}
    obj = parse("/Users/dewey/Desktop/gotest.kmz", res)
    print obj
    print obj.resources
    print res
    
    
    