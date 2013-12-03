'''
Created on Sep 28, 2013

@author: dewey
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import externalreslib.nts as nts
import os

from geolib.geom2d import Bounds



def __smushToporamaThumbnails(pathtofiles, pathout, noneImage):
    def smush(ntsId):
        return "".join(ntsId).lower()
    for tile in nts.tilesByBounds(nts.SCALE_250K, Bounds(-144.1, -47.99, 40.1, 87.99)):
        ntsId250 = nts.ntsId(nts.SCALE_250K, tile)
        tiles50k = nts.__tiles50ByTile250(tile)
        filenames = []
        ntsIds = []
        notFound = 0
        if ntsId250[0] is not None:
            print ntsId250
            for tile50k in tiles50k:
                ntsId = nts.ntsId(nts.SCALE_50K, tile50k)
                ntsIds.append(smush(ntsId))
                filename = pathtofiles + ("toporama_%s_tn.jpg" % (smush(ntsId)))
                if not os.path.isfile(filename):
                    filename = noneImage
                    notFound += 1
                filenames.append(filename)
            if notFound != len(tiles50k):
                filenameIndex = 0
                bigImage = QImage(600, 480, QImage.Format_ARGB32)
                for imageX in range(4):
                    for imageY in range(4):
                        pxOffsetX = 150 * imageX
                        pxOffsetY = 480 - 120 * imageY
                        tn = QImage(filenames[filenameIndex])
                        for pxX in range(tn.width()):
                            for pxY in range(tn.height()):
                                bigImage.setPixel(pxOffsetX+pxX, pxOffsetY-120+pxY, tn.pixel(pxX, pxY))
                        filenameIndex += 1
                bigFileName = pathout + ("toporama_%s.png" % (smush(ntsId250),))
                bigImage.save(bigFileName)
                print "Saved" + bigFileName

def __smushToporamaSeries(pathtofiles, pathout, noneImage):
    def smush(ntsId):
        return "".join(ntsId).lower()
    for tile in nts.tilesByBounds(nts.SCALE_SERIES, nts.BOUNDS):
        seriesId = nts.ntsId(nts.SCALE_SERIES, tile)
        print seriesId
        notFound = 0
        filenames = []
        tiles250k = nts.__tiles250ByTileSeries(tile)
        for tile250k in tiles250k:
            ntsId = nts.ntsId(nts.SCALE_250K, tile250k)
            filename = pathtofiles + ("toporama_%s.jpg" % smush(ntsId))
            if not os.path.isfile(filename):
                filename = noneImage
                notFound += 1
            filenames.append(filename)
            
        if notFound != len(tiles250k):
                filenameIndex = 0
                if tile[1] >= 7:
                    mapsWidth = 2
                else:
                    mapsWidth = 4
                bigImage = QImage(mapsWidth * 600, 1920, QImage.Format_RGB32)
                for imageX in range(mapsWidth):
                    for imageY in range(4):
                        pxOffsetX = 600 * imageX
                        pxOffsetY = 1920 - 480 * imageY
                        tn = QImage(filenames[filenameIndex])
                        for pxX in range(tn.width()):
                            for pxY in range(tn.height()):
                                bigImage.setPixel(pxOffsetX+pxX, pxOffsetY-480+pxY, tn.pixel(pxX, pxY))
                        filenameIndex += 1
                bigFileName = pathout + ("toporama_%s.jpg" % seriesId)
                
                bigImage.scaled(180*mapsWidth, 480).save(bigFileName)
                print "Saved" + bigFileName
    

def moveThumbs(source, destination):
    for (dirpath, dirnames, filenames) in os.walk(source):
        for f in filenames:
            if f.endswith("_tn.jpg"):
                print "Moving" + f
                os.rename(dirpath + f, destination + f)
                
moveThumbs("/Users/dewey/Desktop/images/", "/Users/dewey/Desktop/images_tn/")
#__smushToporamaThumbnails("/Users/dewey/Desktop/images/", "/Users/dewey/Desktop/images250png/", "/Users/dewey/Desktop/0noneimage.png")        
#__smushToporamaSeries("/Users/dewey/Desktop/images250/", "/Users/dewey/Desktop/imagesSeries/", "/Users/dewey/Desktop/0noneimagebig.jpg")