'''
Created on Sep 25, 2013

@author: dewey
'''
from __future__ import division


_UNITS = dict(m=1, km=1000, ft=0.3048, cm=0.01, mi=1609.34, yd=0.9144, inch=0.0254,
              m2=1, km2=1000000, ft2=.09290304, cm2=0.0001, mi2=2589975.2356, yd2=0.83612736, in2=0.00064516, ha=10000, acre=4046.86)
_UNITS["in"] = _UNITS["inch"]

_LABELS = dict(m="metres", km="kilometres", ft="feet", cm="centimetres", mi="miles", yd="yards", inch="inches",
              m2="square metres", km2="square kilometres", ft2="square feet", cm2="square centimetres",
              mi2="square miles", yd2="square yards", in2="square inches", ha="hectares", acre="acres")
_LABELS["in"] = "inches"

lengthUnits = ("km", "m", "cm", "mi", "yd", "ft", "in")
areaUnits = ("km2", "ha", "m2", "cm2", "mi2", "acre", "yd2", "ft2", "in2")

CATEGORY_METRIC = 1
CATEGORY_IMPERIAL = 2

DIMENTION_LENGTH = 2
DIMENTION_AREA = 4

def getUnits(category, dimention):
    if category == CATEGORY_METRIC and dimention == DIMENTION_LENGTH:
        pass
    if category == CATEGORY_METRIC and dimention == DIMENTION_AREA:
        pass
    if category == CATEGORY_IMPERIAL and dimention == DIMENTION_LENGTH:
        pass
    if category == CATEGORY_IMPERIAL and dimention == DIMENTION_AREA:
        pass

def convertTo(value, unit):
    '''Converts a value from SI units to given unit'''
    return value / _UNITS[unit]

def convertFrom(value, unit):
    '''Converts a value from unit to SI units'''
    return value * _UNITS[unit]

def label(unit):
    return _LABELS[unit]