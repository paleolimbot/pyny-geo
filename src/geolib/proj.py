'''
Created on Oct 3, 2013

@author: dewey
'''
from __future__ import division
from .geom2d import Line, Polygon, PointSeries, Bounds, ComplexPolygon
from math import *


def wrapLongitude(x):
    if x > 180:
        x -= 360
    elif x < -180:
        x += 360
    return x

class LatLonBounds(Bounds):
    '''Bounds that should handle wrapping around the backside of the earth,
    including XY objects that contain values greater than 180 or -180 for X
    values. Does not handle polar regions where latitude wraps around 90 degrees.'''
    
    def __init__(self, minx, maxx, miny, maxy):
        super(LatLonBounds, self).__init__(minx, maxx, miny, maxy)
        
    def width(self):
        superWidth = Bounds.width(self)
        if superWidth < 0:
            return superWidth + 360
        else:
            return superWidth
    
    def contains(self, point):
        for bounds in self.splitToValidBounds():
            if bounds.contains(point):
                return True
        return False
    
    def wrapsLon(self):
        superWidth = Bounds.width(self)
        return  superWidth < 0
    
    def splitToValidBounds(self):
        '''Returns a tuple of 1 or 2 Bounds objects on either side of the -180 meridian if needed'''
        if self.wrapsLon():
            maxx1 = 180
            minx2 = -180
            return (Bounds(self.minx(), maxx1, self.miny(), self.maxy()), Bounds(minx2, self.maxx(), self.miny(), self.maxy()))
        else:
            return (self,)
        
    @staticmethod
    def fromPoints(point1, point2):
        miny = min(point1[1], point2[1])
        maxy = max(point1[1], point2[1])
        minx = point1[0]
        maxx = point2[0]
        return LatLonBounds(minx, maxx, miny, maxy)

class Ellipsoid(object):
    
    def __init__(self, equatorRadius, poleRadius=None, name=None, shortName=None):
        
        self.__equatorRadius = equatorRadius
        if poleRadius is None:
            poleRadius = equatorRadius
        self.__poleRadius = poleRadius
        self.__eccentricitySquared = 1.0 - (poleRadius * poleRadius) / (equatorRadius * equatorRadius);
        self.__eccentricity = sqrt(self.__eccentricitySquared)
        self.__name = name
        self.__shortName = name
    
    def poleRadius(self):
        return self.__poleRadius
    def equatorRadius(self):
        return self.__equatorRadius
    def eccentricity(self):
        return self.__eccentricity
    def eccentricitySquared(self):
        return self.__eccentricitySquared
    def rMajor(self):
        return self.equatorRadius()
    def rMinor(self):
        return self.poleRadius()
    def reciprocalFlattening(self):
        return self.rMajor() / (self.rMajor() - self.rMinor())
    def flattening(self):
        return 1 / self.reciprocalFlattening()
    
    def radiusAt(self, latitude):
        a = self.rMajor()
        b = self.rMinor()
        f = latitude
        rSquared = ( ((a**2)*cos(f))**2 + ((b**2)*sin(f))**2 ) / ( (a*cos(f))**2 + (b*sin(f))**2 )
        return sqrt(rSquared)
    
    def __repr__(self):
        return "Ellipsoid(%f, %f)" % (self.equatorRadius(), self.poleRadius())
    
    def __str__(self):
        return `self`
    
    @staticmethod
    def byReciprocalFlattening(equatorRadius, reciprocalFlattening, name=None, shortName=None):
        f = 1.0 / reciprocalFlattening
        eccentricity2 = 2 * f - f * f;
        return Ellipsoid.byEccentricitySquared(equatorRadius, eccentricity2, name, shortName)
    
    @staticmethod
    def byEccentricitySquared(equatorRadius, eccentricitySquared, name=None, shortName=None):
        poleRadius = equatorRadius * sqrt(1.0 - eccentricitySquared)
        return Ellipsoid(equatorRadius, poleRadius, name, shortName)

class Ellipsoids(object):

    def __init__(self):
        pass

    SPHERE = Ellipsoid(6371008.7714)
    WGS84 = Ellipsoid.byReciprocalFlattening(6378137.0, 298.257223563)
    GRS1980 = Ellipsoid.byReciprocalFlattening(6378137.0, 298.257222101)

class Projection(object):
    '''Base class for projections that transform lat/lon information into projected information.'''
    def __init__(self, ellipsoid, falseEasting=0, falseNorthing=0):
        self.__ellipsoid = ellipsoid
        self.__falseEasting = falseEasting
        self.__falseNorthing = falseNorthing
        self.__epsg = 0
    
    def falseEasting(self):
        return self.__falseEasting
    
    def falseNorthing(self):
        return self.__falseNorthing

    def setEpsg(self, epsg):
        self.__epsg = epsg
    
    def epsg(self):
        return self.__epsg
    
    def ellipsoid(self):
        return self.__ellipsoid
    
    def latLonBounds(self):
        '''Returns a Bounds object defining the maximum lat/lon extent to which this projection applies.'''
        return NotImplementedError
    
    def projectedBounds(self):
        '''Returns a Bounds object defining the maximum projected extent to which this projection applies.'''
        return NotImplementedError
    
    def projectX(self, lon, lat):
        raise NotImplementedError
    
    def projectY(self, lon, lat):
        raise NotImplementedError
    
    def inverseProjectX(self, x, y):
        raise NotImplementedError
    
    def inverseProjectY(self, x, y):
        raise NotImplementedError
    
    def projectPoint(self, point, wrapX=False):
        newX = self.projectX(point[0], point[1]) + self.falseEasting()
        newY = self.projectY(point[0], point[1]) + self.falseNorthing()
        return (newX, newY)
    
    def inverseProjectPoint(self, point, wrapLon=False):
        x = point[0]-self.falseEasting()
        y = point[1]-self.falseNorthing()
        return (self.inverseProjectX(x, y), self.inverseProjectY(x, y))
    
    def project(self, *points):
        '''Takes one or more XY objects containing lat/lon information and
        returns a list of the same length containing projected XY objects.
        Raises a ProjectionError if there is an error.'''
        if len(points) == 1:
            return self.projectPoint(points[0])
        elif len(points) > 1:
            return [self.projectPoint(point) for point in points]

    def inverseProject(self, *points):
        '''Takes one or more XY objects containing projected points and
        returns a list of the same length lat/lon XY objects.
        Raises a ProjectionError if there is an error.'''
        if len(points) == 1:
            return self.inverseProjectPoint(points[0])
        elif len(points) > 1:
            return [self.inverseProjectPoint(point) for point in points]
    
    def projectLine(self, line):
        start, end = self.project(line.start(), line.end())
        return Line(start, end)
    
    def projectPointSeries(self, series):
        projectedPoints = self.project(*series)
        return PointSeries(projectedPoints)

    def projectPolygon(self, polygon):
        projectedPoints = self.project(*polygon)
        return Polygon(projectedPoints)
    
    def projectBounds(self, bounds, wrapLon=True):
        lowerLeft = self.projectPoint(bounds.bottomLeft(), wrapLon)
        upperRight = self.projectPoint(bounds.topRight(), wrapLon)
        return Bounds.fromPoints(lowerLeft, upperRight)
    
    def projectComplexPolygon(self, polygon):
        outerPoints = self.project(*polygon)
        interiorPolys = []
        for interiorPoly in polygon.interiorPolygons():
            interiorPolys.append(self.projectPolygon(interiorPoly))
        return ComplexPolygon(outerPoints, *interiorPolys)
    
    def inverseProjectLine(self, line):
        start, end = self.inverseProject(line.start(), line.end())
        return Line(start, end)
    
    def inverseProjectPointSeries(self, series):
        projectedPoints = self.inverseProject(*series)
        return PointSeries(projectedPoints)
    
    def inverseProjectPolygon(self, polygon):
        projectedPoints = self.inverseProject(*polygon)
        return Polygon(projectedPoints)
    
    def inverseProjectComplexPolygon(self, polygon):
        outerPoints = self.inverseProject(*polygon)
        interiorPolys = []
        for interiorPoly in polygon.interiorPolygons():
            interiorPolys.append(self.inverseProjectPolygon(interiorPoly))
        return ComplexPolygon(outerPoints, *interiorPolys)
    
    def inverseProjectBounds(self, bounds, ignoreProjBounds=False):
        lowerLeft = self.inverseProjectPoint(bounds.bottomLeft(), ignoreProjBounds)
        upperRight = self.inverseProjectPoint(bounds.topRight(), ignoreProjBounds)
        return LatLonBounds.fromPoints(lowerLeft, upperRight)
    
class LatLonProjection(Projection):
    
    def __init__(self):
        Projection.__init__(self, None)

    def latLonBounds(self):
        return Bounds(-180, 180, -90, 90)
    
    def projectedBounds(self):
        return self.latLonBounds()
    
    def projectX(self, lon, lat):
        return lon
    
    def projectY(self, lon, lat):
        return lat
    
    def inverseProjectX(self, x, y):
        return x
    
    def inverseProjectY(self, x, y):
        return y
    
class CylindricalProjection(Projection):
    
    def __init__(self, ellipsoid, centralMeridian=0, falseEasting=0, falseNorthing=0):
        Projection.__init__(self, ellipsoid, falseEasting, falseNorthing)
        self.__centralMeridian = centralMeridian
    
    def latLonBounds(self):
        return LatLonBounds(-180, 180, -89, 89)
    
    def projectedBounds(self):
        return Bounds(self.projectX(-180, 0), self.projectX(180,0), self.projectY(0,-89), self.projectY(0, 89))
        
    def centralMeridian(self):
        return self.__centralMeridian
     
    def projectPoint(self, point, wrapLon=False):
        lon = point[0]-self.centralMeridian()
        lat = point[1]
        if wrapLon:
            lon = wrapLongitude(lon)
        return Projection.projectPoint(self, (lon, lat))
    
    def inverseProjectPoint(self, point, wrapLon=False):
        latlon = Projection.inverseProjectPoint(self, point, wrapLon)
        newLon = latlon[0] + self.centralMeridian()
        newLat = latlon[1]
        if wrapLon:
            newLon = wrapLongitude(newLon)
        return (newLon, newLat)

class MercatorProjection(CylindricalProjection):
    
    def __init__(self, ellipsoid, centralMeridian=0, falseEasting=0, falseNorthing=0):
        CylindricalProjection.__init__(self, ellipsoid, centralMeridian, falseEasting, falseNorthing)
    
    def projectX(self, lon, lat):
        el = self.ellipsoid()
        return el.rMajor()*radians(lon)
    
    def projectY(self, lon, lat):
        el = self.ellipsoid()
        phi = radians(lat)
        sinphi = sin(phi)
        con = el.eccentricity()*sinphi
        com = el.eccentricity()/2
        con = ((1.0-con)/(1.0+con))**com
        ts = tan((pi/2-phi)/2)/con
        return 0-el.rMajor()*log(ts)
    
    def inverseProjectX(self, x, y):
        el = self.ellipsoid()
        return degrees(x / el.rMajor())
    
    def inverseProjectY(self, x, y):
        el = self.ellipsoid()
        ts = exp(-y / el.rMajor());
        phi = (pi/2) - 2 * atan(ts);
        for i in range(15):
            str(i)
            con = el.eccentricity() * sin(phi);
            dphi = (pi/2) - 2 * atan(ts * (((1.0 - con) / (1.0 + con))** (el.eccentricity()/2))) - phi;
            phi += dphi;
            if fabs(dphi) <= 0.000000001:
                break
        return degrees(phi)

class GoogleMapsProjection(CylindricalProjection):
        
    def __init__(self, centralMeridian=0):
        CylindricalProjection.__init__(self, None, centralMeridian)
    
    def inverseProjectX(self, x, y):
        return x
    def projectX(self, lon, lat):
        return lon
    def inverseProjectY(self, x, y):
        return 180.0/pi*(2.0*atan(exp(y*pi/180.0))-pi/2.0)
    def projectY(self, lon, lat):
        return 180.0/pi*log(tan(pi/4.0+lat*(pi/180.0)/2.0))

class CylindricalEqualAreaProjection(CylindricalProjection):
    
    def __init__(self, ellipsoid, centralMeridian=0, standardLatitude=0, falseEasting=0, falseNorthing=0):
        CylindricalProjection.__init__(self, ellipsoid, centralMeridian, falseEasting, falseNorthing)
        self.__cosPhi0 = cos(radians(standardLatitude))
        
    def cosphi0(self):
        return self.__cosPhi0
    
    def inverseProjectX(self, x, y):
        el = self.ellipsoid()
        return degrees((x / el.rMajor()) / self.cosphi0())
    def projectX(self, lon, lat):
        el = self.ellipsoid()
        return self.cosphi0() * radians(lon) * el.rMajor()
    def inverseProjectY(self, x, y):
        el = self.ellipsoid()
        cosPhiY = self.cosphi0() * (y / el.rMajor())
        return degrees(asin(cosPhiY))
    def projectY(self, lon, lat):
        el = self.ellipsoid()
        return sin(radians(lat)) / self.cosphi0() * el.rMajor()
        
class TransverseMercatorProjection(Projection):
    
    def __init__(self, ellipsoid, grid0Meridian=0, grid0MeridianScale=1, grid0Latitude=0, falseEasting=0, falseNorthing=0):
        Projection.__init__(self, ellipsoid, falseEasting, falseNorthing)
        self.__grid0Meridian = grid0Meridian
        self.__grid0MeridianScale = grid0MeridianScale
        self.__grid0Latitude = grid0Latitude
        self.__hParams = self.calcHParams()
        self.__inverseHParams = self.calcInverseHParams()
        self.__commonParams = self.calcCommonParams()
    
    def latLonBounds(self):
        return LatLonBounds(wrapLongitude(-89+self.grid0Meridian()), wrapLongitude(89+self.grid0Meridian()), -90, 90)
    
    def projectedBounds(self):
        return self.projectBounds(self.latLonBounds())
    
    def calcCommonParams(self):
        h1, h2, h3, h4 = self.__hParams
        
        phi0 = radians(self.grid0Latitude())
        k0 = self.grid0MeridianScale()
        
        a = self.ellipsoid().rMajor()
        e = self.ellipsoid().eccentricity()
        f = self.ellipsoid().flattening()
        n = f / (2-f)
        
        B = (a/(1+n)) * (1+ n**2/4.0 + n**4/64.0)
        Q0 = asinh(tan(phi0)) - (e * atanh(e * sin(phi0)))
        beta0 = atan(sinh(Q0))
        st00 = asin(sin(beta0))
        
        st01 = h1 * sin(2*st00) 
        st02 = h2 * sin(4*st00) 
        st03 = h3 * sin(6*st00) 
        st04 = h4 * sin(8*st00) 
        
        M0 = B * (st00 + st01 + st02 + st03 + st04)
        
        return e, B, M0, k0
    
    def calcHParams(self):
        f = self.ellipsoid().flattening()
        n = f / (2-f)
        h1 = (n/2.0) - ((2.0/3.0) * n**2) + ((5.0/16.0) * n**3) + ((41.0/180.0) * n**4)
        h2 = ((13.0/48.0) * n**2) - ((3.0/5.0) * n**3) + (557.0/1440.0) * n**4
        h3 = ((61.0/240.0) * n**3) - ((103.0/140.0) * n**4)
        h4 = (49561.0/161280.0) * n**4
        return h1, h2, h3, h4
    
    def calcInverseHParams(self):
        f = self.ellipsoid().flattening()
        n = f / (2-f)
        h1p = (n/2.0) - ((2.0/3.0) * n**2) + ((37.0/96.0) * n**3) - ((1.0/360.0) * n**4)
        h2p = ((1.0/48.0) * n**2) + ((1/15.0) * n**3) - ((437.0/1440.0) * n**4)
        h3p = ((17.0/480.0) * n**3) - ((37.0/840.0) * n**4)
        h4p = (4397.0/161280.0) * n**4
        return h1p, h2p, h3p, h4p
    
    def projectPoint(self, latLonPoint, wrapLon=False):
        h1, h2, h3, h4 = self.__hParams
        e, B, M0, k0 = self.__commonParams
        
        phi = radians(latLonPoint[1])
        lonRad = radians(latLonPoint[0]-self.grid0Meridian())
        
        Q = asinh(tan(phi)) - (e * atanh(e * sin(phi)))
        beta = atan(sinh(Q))
       
        nu0 = atanh(cos(beta) * sin(lonRad))
        st0 = asin(sin(beta) * cosh(nu0))
        
        st1 = h1 * sin(2*st0) * cosh(2*nu0)
        st2 = h2 * sin(4*st0) * cosh(4*nu0)
        st3 = h3 * sin(6*st0) * cosh(6*nu0)
        st4 = h4 * sin(8*st0) * cosh(8*nu0)
        
        st = st0 + st1 + st2 + st3 + st4
        
        nu1 = h1 * cos(2*st0) * sinh(2 * nu0)
        nu2 = h2 * cos(4*st0) * sinh(4 * nu0)
        nu3 = h3 * cos(6*st0) * sinh(6 * nu0)
        nu4 = h4 * cos(8*st0) * sinh(8 * nu0)
        
        nu = nu0 + nu1 + nu2 + nu3 + nu4
        
        easting = self.falseEasting() + (k0 * B * nu)
        northing = self.falseNorthing() + (k0 * (B * st - M0))
        
        return (easting, northing)
    
    def inverseProjectPoint(self, xyPoint, wrapLon = False):
        h1p, h2p, h3p, h4p = self.__inverseHParams
        e, B, M0, k0 = self.__commonParams
        
        nup = (xyPoint[0] - self.falseEasting()) / (B * k0)
        stp = ((xyPoint[1] - self.falseNorthing()) + (k0 * M0)) / (B * k0)
        
        st1p = h1p * sin(2 * stp) * cosh(2 * nup)
        st2p = h2p * sin(4 * stp) * cosh(4 * nup)
        st3p = h3p * sin(6 * stp) * cosh(6 * nup)
        st4p = h4p * sin(8 * stp) * cosh(8 * nup)
        
        nu1p = h1p * cos(2 * stp) * sinh(2 * nup)
        nu2p = h2p * cos(4 * stp) * sinh(4 * nup)
        nu3p = h3p * cos(6 * stp) * sinh(6 * nup)
        nu4p = h4p * cos(8 * stp) * sinh(8 * nup)
        
        st0p = stp - (st1p + st2p + st3p + st4p)
        nu0p = nup - (nu1p + nu2p + nu3p + nu4p)
        
        betap = asin(sin(st0p) / cosh(nu0p))
        Qp = asinh(tan(betap))
        Qpp = Qp + e * atanh(e * tanh(Qp))
        for index in range(15):
            index += 1 #keeps warning off
            deltaQpp = e * atanh(e * tanh(Qpp))
            Qpp = Qp + deltaQpp
            if abs(deltaQpp) < 0.00000001:
                break
        phi = atan(sinh(Qpp))
        lonRad = asin(tanh(nu0p) / cos(betap))
        
        return (self.grid0Meridian() + degrees(lonRad), degrees(phi))
    
    def grid0Meridian(self):
        return self.__grid0Meridian
    
    def grid0Latitude(self):
        return self.__grid0Latitude
    
    def grid0MeridianScale(self):
        return self.__grid0MeridianScale

class UniversalTransverseMercatorProjection(TransverseMercatorProjection):

    HEMISPHERE_N = "N"
    HEMISPHERE_S = "S"

    def __init__(self, ellipsoid, lonZone, sHemisphere):
        grid0Meridian = -183 + lonZone * 6.0
        TransverseMercatorProjection.__init__(self, ellipsoid, grid0Meridian, 0.9996, 0, 500000, 10000000 if sHemisphere else 0)
        self.__zone = (lonZone, (self.HEMISPHERE_S if sHemisphere else self.HEMISPHERE_N))
    
    def projectedBounds(self):
        return Bounds(0, 1000000, 0, 10000000)
    
    def latLonBounds(self):
        return Bounds(self.grid0Meridian()-3, self.grid0Meridian()+3, -80, 84)
        
    def zone(self):
        return self.__zone

class Projections(object):
    
    def __init__(self):
        pass
    
    LATLON = LatLonProjection()
    UTM_PROJECTIONS = {}

    @staticmethod
    def mercator(centralMeridian=0, ellipsoid=Ellipsoids.WGS84):
        return MercatorProjection(ellipsoid, centralMeridian)
    @staticmethod
    def cylequalarea(centralMeridian=0, standardLat=0, ellipsoid=Ellipsoids.WGS84):
        return CylindricalEqualAreaProjection(ellipsoid, centralMeridian, standardLat)
    @staticmethod
    def googlemaps(centralMeridian=0):
        return GoogleMapsProjection(centralMeridian)
    @staticmethod
    def utm(zoneTuple, ellipsoid=Ellipsoids.WGS84):
        zoneId = (str(zoneTuple[0]) + zoneTuple[1])
        if zoneId in Projections.UTM_PROJECTIONS:
            return Projections.UTM_PROJECTIONS[zoneId]
        else:
            proj = UniversalTransverseMercatorProjection(ellipsoid, zoneTuple[0], zoneTuple[1]=="S")
            Projections.UTM_PROJECTIONS[zoneId] = proj
            return proj
        
    