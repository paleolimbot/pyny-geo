#!/usr/bin/env python
# encoding: utf-8
"""
RMS - Root Mean Squere
----------------------
Counting of Root Mean squere for given points (for given GCPS filename).
Affine transformation is expected on the standard input in the form of WorldFile.

Created by Klokan Petr Pridal, RMS algorithm described at:
http://en.wikipedia.org/wiki/Root_mean_square

Development carried out thanks to R&D grant DC08P02OUK006 - Old Maps Online
(www.oldmapsonline.org) from Ministry of Culture of the Czech Republic

Copyright (c) 2008 OldMapsOnline.org. All rights reserved.
"""

import sys, math


destSet = []
sourceSet = []

if len(sys.argv) == 1:
	print "You have to specify a file with GCPs on the input ('pixel line easting northing' per line)"
	sys.exit(1)

print sys.argv[1]
for line in open(sys.argv[1], 'r'):
    destSet.append( map( float, line.split()[:2] ) )
    sourceSet.append( map( float, line.split()[2:4] ) )

w = []
for line in sys.stdin:
    if line.strip():
        w.append(float(line))


projSet = []
for x,y in sourceSet:
    p = []
    p.append( w[4] + w[0]*x + w[2]*y )
    p.append( w[5] + w[1]*x + w[3]*y )
    projSet.append( p )


errs = []

#print w
#print '--'
for i in range(len(destSet)):
    x,y = destSet[i]
    px,py = projSet[i]
    minx = min( x, px)
    maxx = max( x, px)
    miny = min( y, py)
    maxy = max( y, py)
    sx = maxx - minx
    sy = maxy - miny
    err = math.sqrt( sx*sx + sy*sy )
    errs.append(err)
    print x,y,'-',px,py,'==',err

pow2 = lambda x: x*x

print "RMS:", math.sqrt( sum( map( pow2, errs )) / len(errs) )

