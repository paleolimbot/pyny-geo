'''
Created on Oct 1, 2013

@author: dewey
'''
import os
import urllib
import xml.sax
import tempfile
from xml.sax import ContentHandler
from HTMLParser import HTMLParser
from geolib.geom2d import Bounds

"""http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/-/AND/(urn:iso:series)1996-population-ecumene-census-data-canada/(urn:iso:type)publication/?
    q=keywords&bbox=-64.5,45,-64,45.25&published-min=1900-01-01&published-max=1900-12-31&entry-type=full&max-results=50&alt=rss"""

URL_BASE = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/"

SERIES_PREFIX = "(urn:iso:series)"
TYPE_PREFIX = "(urn:iso:type)"
AUTHOR_PREFIX = "(urn:atom:author)"

TYPE_MAPS = "maps"
TYPE_DATA = "data"
#TYPE_REMOTE_SENSING = None - does not change URL for some reason
TYPE_ELEVATION = "elevation"
TYPE_PUBLICATION = "publication"
  
ARG_KEYWORDS = "q"
ARG_BOUNDS = "bbox"
ARG_PUBLISHED_MIN = "published-min"
ARG_PUBLISHED_MAX = "published-max"
ARG_ENTRY_TYPE = "entry-type"
ENTRY_TYPE_FULL = "full"

ARG_MAX_RESULTS = "max-results"
ARG_ALT = "alt" #should always equal "rss" for rss feeds, web result otherwise
ALT_RSS = "rss"

ARG_TYPE = "__TYPE"
ARG_SERIES = "__SERIES"
ARG_AUTHOR = "__AUTHOR"

def __formatAuthor(unformatted):
    out = " ".join(unformatted.split())
    out = out.lower().strip(",.")
    return out.replace(" ", "-")

def __urlFromArgs(args):
    extraArgs = 0
    if args.has_key(ARG_TYPE):
        dataType = args[ARG_TYPE]
        del args[ARG_TYPE]
        extraArgs += 1
    else:
        dataType = None
    
    if args.has_key(ARG_SERIES):
        series = args[ARG_SERIES]
        del args[ARG_SERIES]
        extraArgs += 1
    else:
        series = None
    
    if args.has_key(ARG_AUTHOR):
        author = args[ARG_AUTHOR]
        del args[ARG_AUTHOR]
        extraArgs += 1
    else:
        author = None
    
    queryString = urllib.urlencode(args)
    
    base = URL_BASE
    if extraArgs > 0:
        base += "-/"
    if extraArgs > 1:
        base += "AND/"
    
    if dataType is not None:
        base += TYPE_PREFIX + dataType + "/"
    if series is not None:
        base += SERIES_PREFIX + series + "/"
    if author is not None:
        base += AUTHOR_PREFIX + author + "/"
    
    return base + "?" + queryString

def __generateUrl(bounds=None, keywords=None, dataType=None, author=None, yearRange=None, series=None, maxResults=None, entryType=None, alt=None):
    args = {}
    
    if bounds is not None:
        args[ARG_BOUNDS] = "%f,%f,%f,%f" % (bounds.miny(), bounds.minx(), bounds.maxy(), bounds.maxx())
    if keywords is not None:
        args[ARG_KEYWORDS] = keywords
    if dataType is not None:
        args[ARG_TYPE] = dataType
    if author is not None:
        args[ARG_AUTHOR] = __formatAuthor(author)
    if yearRange is not None:
        if len(yearRange):
            firstDate = str(yearRange[0]) + "-01-01"
            if len(yearRange) >= 2:
                lastDate = str(yearRange[1]) + "-12-31"
            else:
                lastDate = str(yearRange[0]) + "-12-31"
            args[ARG_PUBLISHED_MIN] = firstDate
            args[ARG_PUBLISHED_MAX] = lastDate
    if series is not None:
        args[ARG_SERIES] = series
    if maxResults is not None:
        args[ARG_MAX_RESULTS] = maxResults
    if entryType is not None:
        args[ARG_ENTRY_TYPE] = entryType
    if alt is not None:
        args[ARG_ALT] = alt    
    
    return __urlFromArgs(args)

def rssUrl(bounds=None, keywords=None, dataType=None, author=None, yearRange=None, series=None, maxResults=None, entryType=None):
    return __generateUrl(bounds, keywords, dataType, author, yearRange, series, maxResults, entryType, ALT_RSS)

def webUrl(bounds=None, keywords=None, dataType=None, author=None, yearRange=None, series=None, maxResults=None, entryType=None):
    return __generateUrl(bounds, keywords, dataType, author, yearRange, series, maxResults, entryType, None)

def loadSeriesData():
    def filepath():
        return os.path.dirname(__file__)
    
    class MyHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.insideSelect = False
            self.values = []
            self.titles = []
        
        def attr(self, attrs, name):
            for attr, value in attrs:
                if attr == name:
                    return value
            
        def handle_starttag(self, tag, attrs):
            if tag == "select":
                iId = self.attr(attrs, "id")
                if iId == "selSeries":
                    self.insideSelect = True
            elif tag == "option" and self.insideSelect:
                value = self.attr(attrs, "value")
                title = self.attr(attrs, "title")
                if value and title:
                    if value != "0":
                        self.values.append(value)
                        self.titles.append(title)
        def handle_endtag(self, tag):
            if tag == "select" and self.insideSelect:
                self.insideSelect = False
            
    parser = MyHTMLParser()
    
    handle = open(filepath() + os.sep + "geogratis_series.xml")
    parser.feed(handle.read())
    handle.close()
    return parser.values, parser.titles

class RssFeed(object):
    
    ITEM = "item"
    
    TITLE = "title"
    LINK = "link"
    PUBDATE = "pubDate"
    AUTHOR = "author"
    DESCRIPTION = "description"
    GEORSSPOLYGON = "georss:polygon"
    
    def __init__(self):
        self.items = []
        self.info = {}
    

class RssHandler(ContentHandler):
        def __init__(self):
            ContentHandler.__init__(self)
            self.chars = ""
            self.currentTag = None
            self.feed = RssFeed()
            self.item = None
        
        def set(self, attribute, value):
            if self.item is not None:
                self.item[attribute] = value
            else:
                self.feed.info[attribute] = value
         
        @staticmethod    
        def parseGeoRssPolygon(string):
            coords = string.split()
            points = []
            for index in range(0, 2, len(coords)):
                coord1 = coords[index]
                if index+1 < len(coords):
                    coord2 = coords[index+1]
                    points.append((coord2, coord1))
            
            if len(points):
                return Bounds.fromPoints(*points)
            else:
                return None
                    
        
        def startElement(self, name, attrs):
            self.chars = ""
            if name == RssFeed.ITEM:
                self.item = {}


        def endElement(self, currentName):
            if currentName == RssFeed.TITLE:
                self.set(currentName, self.chars)
            elif currentName == RssFeed.LINK:
                self.set(currentName, self.chars)
            elif currentName == RssFeed.PUBDATE:
                self.set(currentName, self.chars)
            elif currentName == RssFeed.AUTHOR:
                self.set(currentName, self.chars)
            elif currentName == RssFeed.DESCRIPTION:
                self.set(currentName, self.chars)
            elif currentName == RssFeed.GEORSSPOLYGON:
                poly = self.parseGeoRssPolygon(self.chars)
                if poly is not None:
                    self.set(currentName, poly)
            elif currentName == RssFeed.ITEM:
                self.feed.items.append(self.item)
                self.item = None
            self.chars = ""


        def characters(self, content):
            self.chars += content


def parseRssResult(filename):
    handle = open(filename)
    handler = RssHandler()
    xml.sax.parse(handle, handler)
    feed = handler.feed
    handle.close()
    return feed

def downloadAndParseRss(bounds=None, keywords=None, dataType=None, author=None, yearRange=None, series=None, maxResults=None, entryType=None):
    url = rssUrl(bounds, keywords, dataType, author, yearRange, series, maxResults, entryType)
    tempf = tempfile.mkstemp()[1]
    if urllib.urlretrieve(url, tempf):
        return parseRssResult(tempf)
    else:
        raise IOError, "download of rss failed " + url

