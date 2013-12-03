'''
Created on Oct 2, 2013

@author: dewey
'''

SUB_LSD_MAP = (("B", "A"),
               ("C", "D"))

LSD_MAP = ((4, 3, 2, 1),
           (5, 6, 7, 8),
           (12, 11, 10, 9),
           (13, 14,15,16))

SECTION_MAP = ((6, 5, 4, 3, 2, 1),
               (7, 8, 9, 10, 11, 12),
               (18, 17, 16, 15, 14, 13),
               (19, 20, 21, 22, 23, 24),
               (30, 29, 28, 27, 26, 25),
               (31, 32, 33, 34, 35, 36))

def __idFrom(parentBounds, idMap, xDiv, yDiv, point):
    subBounds = parentBounds.subdivide(xDiv, yDiv)
    for x in range(xDiv):
        for y in range(yDiv):
            if subBounds[x][y].contains(point):
                return LSD_MAP[y][x]
    return None

def __sectionLsdFrom(twpBounds, point):
    pass