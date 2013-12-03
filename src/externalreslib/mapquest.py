'''
Created on Oct 1, 2013

@author: dewey
'''
import urllib
import tempfile
import json

from geolib.geom2d import XY

URL_GEOCODE = "http://www.mapquestapi.com/geocoding/v1/address"
URL_REVERSE = "http://www.mapquestapi.com/geocoding/v1/reverse"

ARG_MAX_RESULTS = "maxResults"
ARG_THUMB_MAPS = "thumbMaps"
ARG_BOUNDING_BOX = "boundingBox"
ARG_IGNORE_LAT_LON_INPUT = "ignoreLatLngInput"
ARG_API_KEY = "key"
ARG_LOCATION = "location"
ARG_JSON_REQ = "json"
ARG_XML_REQ = "xml"
ARG_IN_FORMAT = "inFormat"
ARG_OUT_FORMAT = "outFormat"
ARG_CALLBACK = "callback"

FORMAT_JSON = "json"
FORMAT_XML = "xml"

INFO = "info"

INFO_STATUS_CODE = "statuscode"
STATUS_CODE_OK = 0
STATUS_CODE_ERROR_INPUT = 400
STATUS_CODE_KEY_ERROR = 403
STATUS_CODE_UNKNOWN = 500

INFO_MESSAGES = "messages"
INFO_COPYRIGHT = "copyright"
INFO_IMAGE_URL = "imageUrl"



RESULTS = "results"
RESULTS_LOCATIONS = "locations"
RESULTS_PROVIDED_LOCATION = "providedLocation"


LOCATION_LAT_LON = "latLng"
LOCATION_LOCATION = "location"
LOCATION_STREET = "street"
LOCATION_CITY = "adminArea5"
LOCATION_COUNTY = "adminArea4"
LOCATION_STATE_PROV = "adminArea3"
LOCATION_COUNTRY = "adminArea1"
LOCATION_POSTAL = "postalCode"
LOCATION_TYPE = "type" 
LOCATION_DRAG_POINT = "dragPoint"
LOCATION_DISPLAY_LAT_LON = "displayLatLng"
LOCATION_QUALITY = "geocodeQuality"
LOCATION_QUALITY_CODE = "geocodeQualityCode"

GRANULARITY_POINT = "P1"
GRANULARITY_ADDRESS = "L1"
GRANULARITY_INTERSECTION = "I1"
GRANULARITY_BLOCK = "B1"
GRANULARITY_STREET = "B2"
GRANULARITY_POSSIBLE_BLOCK = "B3"
GRANULARITY_COUNTRY = "A1"
GRANULARITY_STATE = "A3"
GRANULARITY_COUNTY = "A4"
GRANULARITY_CITY = "A5"
GRANULARITY_ZIP = "Z1"
GRANULARITY_ZIP2 = "Z2"
GRANULARITY_ZIP3 = "Z3"
GRANULARITY_ZIP4 = "Z4"

GRANULARITY_RANK = (GRANULARITY_COUNTRY, GRANULARITY_STATE, GRANULARITY_COUNTY, GRANULARITY_CITY, GRANULARITY_ZIP,
                    GRANULARITY_ZIP2, GRANULARITY_ZIP3, GRANULARITY_ZIP4, GRANULARITY_STREET, GRANULARITY_BLOCK,
                    GRANULARITY_POSSIBLE_BLOCK, GRANULARITY_INTERSECTION, GRANULARITY_ADDRESS, GRANULARITY_POINT)
GRANULARITY_ZOOM = ((4, 5),(5, 6),(7, 9),(10, 13),(13,14),(13.5,14),(14,15),(14, 15),(14,15),(14, 15),(14, 15),(14, 15),(14, 15),(14, 15))

CONFIDENCE_EXACT = "A"
CONFIDENCE_GOOD = "B"
CONFIDENCE_APPROX = "C"
CONFIDENCE_NONE = "X"

LOCATION_LINKID = "linkId"
LOCATION_SIDE_OF_STREET = "sideOfStreet"

def __parseLatLng(args):
    if args.has_key("lat") and args.has_key("lng"):
        return (args["lng"], args["lat"])
    else:
        return None

def point(locationDict):
    return __parseLatLng(locationDict[LOCATION_LAT_LON])

def summary(locationDict):
    street = locationDict[LOCATION_STREET].strip()
    city = locationDict[LOCATION_CITY].strip()
    state = locationDict[LOCATION_STATE_PROV].strip()
    if len(state) > 0 and len(city) > 0 and len(street) > 0:
        return "%s, %s %s" % (street, city, state)
    elif len(state) > 0 and len(city) > 0:
        return "%s %s" % (city, state)
    elif len(state) > 0:
        return state
    else:
        return None

def zoomRange(locationDict):
    quality = locationDict[LOCATION_QUALITY_CODE].strip()
    if len(quality) > 0:
        code = quality[:2]
        try:
            index = GRANULARITY_RANK.index(code)
            return GRANULARITY_ZOOM[index]
        except ValueError:
            return None
    else:
        return None
    
    

class GeocodeResult(object):
    
    def __init__(self, resultDict):
        self.info = resultDict
    
    def resultCode(self):
        return self.info[INFO][INFO_STATUS_CODE]
    
    def resultOk(self):
        return self.resultCode() == STATUS_CODE_OK
    
    def message(self, index=0):
        return self.info[INFO][INFO_MESSAGES][index]
    
    def results(self, index=0):
        return self.info[RESULTS][index]
    
    def locations(self, resultsIndex=0):
        return self.results(resultsIndex)[RESULTS_LOCATIONS]
    
    def searchLocation(self, resultsIndex=0):
        return self.results(resultsIndex)[RESULTS_PROVIDED_LOCATION]
    
    def location(self, index=0, resultsIndex=0):
        if index < self.count():
            return self.locations(resultsIndex)[index]
        else:
            return None
    
    def count(self):
        return len(self.locations())
    
    def point(self, index=0, resultsIndex=0):
        if index < self.count():
            return point(self.location(index, resultsIndex))
        else:
            return None
    
    def summary(self, index=0, resultsIndex=0):
        if index < self.count():
            return summary(self.location(index, resultsIndex))
        else:
            return None
    
    def zoomRange(self, index=0, resultsIndex=0):
        if index < self.count():
            return zoomRange(self.location(index, resultsIndex))
        else:
            return None

def __query(argsDict, baseUrl):
    queryString = urllib.urlencode(argsDict)
    url = baseUrl +  "?" + queryString
    filename = tempfile.mkstemp()[1]
    urllib.urlretrieve(url, filename)
    responseF = open(filename)
    response = responseF.read()
    responseF.close()
    results = json.loads(response)
    
    return GeocodeResult(results)


def geocode(apiKey, locationString, bounds=None, maxResults=None):
    args = {}
    args[ARG_API_KEY] = apiKey
    args[ARG_LOCATION] = locationString
    
    args[ARG_OUT_FORMAT] = FORMAT_JSON
    args[ARG_THUMB_MAPS] = "false"
    
    if bounds is not None:
        args[ARG_BOUNDING_BOX] = "%f,%f,%f,%f" % (bounds.miny(), bounds.minx(), bounds.maxy(), bounds.maxx())
    if maxResults is not None:
        args[ARG_MAX_RESULTS] = maxResults
    
    return __query(args, URL_GEOCODE)

def reverseGeocode(apiKey, point, maxResults=None):
    args = {}
    args[ARG_API_KEY] = apiKey
    args[ARG_LOCATION] = "%f,%f" % (point[1], point[0])
    
    args[ARG_OUT_FORMAT] = FORMAT_JSON
    args[ARG_THUMB_MAPS] = "false"
    
    if maxResults is not None:
        args[ARG_MAX_RESULTS] = maxResults
        
    return __query(args, URL_REVERSE)

def __test():
    testLocs = ["36 Acadia st. Wolfville, ns", "restaurant wolfville", "two brothers middlebury", "maddison, wisconsinn"]
    testPoints = [XY(-64.7, 45.04), XY(-71, 45), XY(-110, 52), XY(-110, 37)]
    
    print urllib.unquote("Fmjtd%7Cluubnu62n0%2C2l%3Do5-9uy2g4")
        
    for testLoc in testLocs:
        print testLoc,
        result = geocode("Fmjtd|luubnu62n0,2l=o5-9uy2g4", testLoc)
        print result.resultOk()
        for index in range(result.count()):
            print result.summary(index), result.point(index)
        print ""
      
    for testPoint in testPoints:
        print testPoint,
        result = reverseGeocode("Fmjtd|luubnu62n0,2l=o5-9uy2g4", testPoint)
        print result.resultOk()
        for index in range(result.count()):
            print result.summary(index), result.point(index)
        print ""
