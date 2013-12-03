'''
Created on Aug 21, 2013

@author: dewey
'''
import datetime
from geolib.geom import XY

class NmeaException(Exception):
    pass



class tzinfoUTC(datetime.tzinfo):
    """UTC"""
    ZERO = datetime.timedelta(0)
    HOUR = datetime.timedelta(hours=1)

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.ZERO

def _parseLatLon(stringInput, hem):
    hemispheres = "NESW"
    hem = hem.upper()
    periodPos = stringInput.find(".")
    if periodPos == -1:
        periodPos = len(stringInput)
    if hem in hemispheres:
        minutes = float(stringInput[periodPos-2:])
        deg = int(stringInput[:periodPos-2])
        floatDeg = deg + minutes / 60.0
        if hem == "S" or hem == "W":
            floatDeg *= -1
        return floatDeg
    else:
        raise NmeaException

def _parseUnitsValue(value, unit):
    unitDict = dict(M=1, F=1.8288, f=0.3048, N=1852)
    return float(value)*unitDict[unit]

def _parseUTCTime(stringInput):
    hours = int(stringInput[:2])
    minutes = int(stringInput[2:4])
    seconds = float(stringInput[4:])
    intSeconds = int(seconds)
    milliSeconds = int(round((seconds - intSeconds)*1000.0))
    
    return datetime.time(hours, minutes, intSeconds, milliSeconds, tzinfoUTC())

def _parseDate(stringInput):
    day = int(stringInput[:2])
    month = int(stringInput[2:4])
    year = int(stringInput[4:])
    if 90 < year < 100:
        year += 1900
    elif year < 100:
        year += 2000
    
    return datetime.date(year, month, day)
        

class NmeaFilter(object):
    """Base class to filter NMEA sentences. By default returns True for acceptSentence() for all sentences"""
    def acceptSentence(self, sentence):
        return True
        

class NmeaSentence(object):
    """Class representing an NMEA sentence, defined by talker ID (always first two characters),
    sentence ID (anything after the first two characters and the first comma), computer time received,
    and fields (not including talker ID/sentence ID). Parse sentence by NmeaSentence.parse(), convert to
    sentence by calling str() with the object as the argument. Should be subclassed to provide specific
    methods for accessing more human readable forms of the data."""
    
    def __init__(self, timeReceived, talkerId, sentenceId, fields):
        self.__timeReceived = timeReceived #utc computer time received
        self.__fields = list(fields)
        self.__talkerId = talkerId
        self.__sentenceId = sentenceId
    
    def timeReceived(self):
        return self.__timeReceived
    
    def sentenceCode(self):
        return self.talkerId() + self.sentenceId()
    
    def talkerId(self):
        return self.__talkerId
    
    def sentenceId(self):
        return self.__sentenceId
    
    def fields(self):
        return self.__fields
    
    def __getitem__(self, index):
        return self.__fields.__getitem__(index)
    
    def __iter__(self):
        return self.__fields.__iter__()
    
    def __str__(self):
        fieldString = self.sentenceCode() + "," + ",".join(self)
        return "$" + fieldString + "*" + NmeaSentence.checksumStr(fieldString)
    
    @staticmethod
    def checksum(fieldstring):
        out = 0
        for char in fieldstring:
            out ^= ord(char)
        return out
    
    @staticmethod
    def checksumStr(fieldstring):
        checksum = NmeaSentence.checksum(fieldstring)
        strOut = hex(checksum).replace("0x", "")
        while len(strOut) < 2:
            strOut = "0" + strOut
        return strOut.upper()
    
    @staticmethod
    def parse(string, timeReceived=datetime.datetime.utcnow(), ignoreChecksum=True):
        trimmed = string.strip()
        if trimmed.startswith("$") and trimmed[-3]=="*":
            fieldString = trimmed[1:-3]
            checksum = int(trimmed[-2:], 16)
            fieldStringChecksum = NmeaSentence.checksum(fieldString)
            if(checksum == fieldStringChecksum or ignoreChecksum):
                fields = fieldString.split(",")
                sentenceCode = fields[0]
                talkerId = sentenceCode[:2]
                sentenceId = sentenceCode[2:]
                return NmeaSentence(timeReceived, talkerId, sentenceId, fields[1:])
            else:
                raise NmeaException
        else:
            raise NmeaException
        
        
class NmeaFixSentence(NmeaSentence):
    """Abstract base class for any NMEA sentence representing a current location. Subclasses include
    sentences $--GNS, $--GLL, $--GGA, $--RMC, and $--RMA"""
    
    def __init__(self, sentenceObj):
        if sentenceObj.sentenceId() != self.expectedSentenceId():
            raise NmeaException
        super(NmeaFixSentence, self).__init__(sentenceObj.timeReceived(), sentenceObj.talkerId(), sentenceObj.sentenceId(), sentenceObj.fields())
        self.__xyz = None
    
    def latitude(self):
        hem = self[self.latLonIndicies()[1]].upper()
        latString = self[self.latLonIndicies()[0]]
        return _parseLatLon(latString, hem)
        
    
    def longitude(self):
        hem = self[self.latLonIndicies()[3]].upper()
        lonString = self[self.latLonIndicies()[2]]
        return _parseLatLon(lonString, hem)
    
    def elevation(self):
        if self.elevationFieldIndex() is not None:
            return _parseUnitsValue(self[self.elevationFieldIndex()], self.elevationUnit())
        else:
            return None
    
    def xyz(self):
        if self.__xyz is None:
            elev = self.elevation()
            if elev is not None:
                self.__xyz = XY(self.longitude(), self.latitude(), self.elevation())
            else:
                self.__xyz = XY(self.longitude(), self.latitude())
        return self.__xyz
    
    def utc(self):
        if self.utcFieldIndex() is not None:
            return _parseUTCTime(self[self.utcFieldIndex()])
        else:
            return None
    
    def expectedSentenceId(self):
        raise NotImplementedError
    def latLonIndicies(self):
        #(lat, lathem, lon, lonhem)
        raise NotImplementedError
    def elevationFieldIndex(self):
        raise NotImplementedError
    def elevationUnit(self):
        return "M"
    def utcFieldIndex(self):
        raise NotImplementedError
    def isValid(self):
        raise NotImplementedError
    
class NmeaGNSSentence(NmeaFixSentence):
    
    def __init__(self, sentenceObj):
        super(NmeaGNSSentence, self).__init__(sentenceObj)
    
    def expectedSentenceId(self):
        return "GNS"
    def latLonIndicies(self):
        #(lat, lathem, lon, lonhem)
        return (1, 2, 3, 4)
    def elevationFieldIndex(self):
        return 8
    def utcFieldIndex(self):
        return 0
    def isValid(self):
        return True #unknown what the 'mode' field is
    
class NmeaGLLSentence(NmeaFixSentence):
    
    def __init__(self, sentenceObj):
        super(NmeaGLLSentence, self).__init__(sentenceObj)
    
    def expectedSentenceId(self):
        return "GLL"
    def latLonIndicies(self):
        #(lat, lathem, lon, lonhem)
        return (0, 1, 2, 3)
    def elevationFieldIndex(self):
        return None
    def utcFieldIndex(self):
        return 4
    def isValid(self):
        return self[5] == "A"
    
class NmeaGGASentence(NmeaFixSentence):
    
    def __init__(self, sentenceObj):
        super(NmeaGGASentence, self).__init__(sentenceObj)
    
    def expectedSentenceId(self):
        return "GGA"
    def latLonIndicies(self):
        #(lat, lathem, lon, lonhem)
        return (1, 2, 3, 4)
    def elevationFieldIndex(self):
        return 8
    def utcFieldIndex(self):
        return 0
    def isValid(self):
        return self[5] != "0"
    
class NmeaRMCSentence(NmeaFixSentence):
    
    def __init__(self, sentenceObj):
        super(NmeaRMCSentence, self).__init__(sentenceObj)
    
    def expectedSentenceId(self):
        return "RMC"
    def latLonIndicies(self):
        #(lat, lathem, lon, lonhem)
        return (2, 3, 4, 5)
    def elevationFieldIndex(self):
        return None
    def utcFieldIndex(self):
        return 0
    def isValid(self):
        return self[1] == "A"
    
    def utcTimeDate(self):
        dateObj = _parseDate(self[8])
        utc = self.utc()
        if dateObj is not None and utc is not None:
            return datetime.datetime.combine(dateObj, utc)
        else:
            return None
    
class NmeaRMASentence(NmeaFixSentence):
    
    def __init__(self, sentenceObj):
        super(NmeaRMASentence, self).__init__(sentenceObj)
    
    def expectedSentenceId(self):
        return "RMA"
    def latLonIndicies(self):
        #(lat, lathem, lon, lonhem)
        return (1, 2, 3, 4)
    def elevationFieldIndex(self):
        return None
    def utcFieldIndex(self):
        return None
    def isValid(self):
        return True

class NmeaDepthSentence(NmeaSentence):
    """Class representing $--DBS, $--DBT, and $--DBK sentences."""
    
    def __init__(self, sentenceObj):
        if not sentenceObj.sentenceId() in self.expectedSentenceIds():
            raise NmeaException
        super(NmeaDepthSentence, self).__init__(sentenceObj.timeReceived(), sentenceObj.talkerId(), sentenceObj.sentenceId(), sentenceObj.fields())
        self.__depthMetres = None
    
    def depthMetres(self):
        if self.__depthMetres is None:
            depthM = None
            depthTotal = 0
            depthCount = 0
            
            for index in range(0, 6, 2):
                try:
                    d = (self[index], self[index+1])
                    if len(d[0].strip()) and len(d[1].strip()) :
                        if d[1].strip() == "M":
                            depthM = float(d[0])
                        valM = _parseUnitsValue(d[0], d[1])
                        depthTotal += valM
                        depthCount += 1
                        
                except IndexError:
                    pass
            
            if depthM is not None:
                self.__depthMetres = depthM
            else:
                self.__depthMetres = depthTotal / depthCount
            
        return self.__depthMetres
        
        
    
    def expectedSentenceIds(self):
        return ("DBS", "DBT", "DBK")
    

def test():
    testStrings = ("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",
                   "$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39",
                   "$GPGSV,2,1,08,01,40,083,46,02,17,308,41,12,07,344,39,14,22,228,45*75",
                   "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A",
                   "$GPGLL,4916.45,N,12311.12,W,225444,A,*1D",
                   "$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48",
                   "$GPRMB,A,0.66,L,003,004,4917.24,N,12309.57,W,001.3,052.5,000.5,V*20",
                   "$SDDBT,0017.6,f,2.9,F,005.4,M*78")
    
    gga = NmeaSentence.parse(testStrings[0])
    print NmeaGGASentence(gga).xyz(), NmeaGGASentence(gga).utc()
    
    rmc = NmeaSentence.parse(testStrings[3])
    sent = NmeaRMCSentence(rmc)
    print sent.xyz(), sent.utcTimeDate()
    
    gll = NmeaSentence.parse(testStrings[-4])
    print NmeaGLLSentence(gll).xyz()
    
    dbt = NmeaSentence.parse(testStrings[-1])
    sent = NmeaDepthSentence(dbt)
    print sent.depthMetres()
    
    for string in testStrings:
        s = NmeaSentence.parse(string)
        print s
    
    print "done"
    
test()
        
        