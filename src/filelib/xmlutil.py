'''
Created on Oct 22, 2013

@author: dewey
'''

import re

CDATA_OPEN = u"<![CDATA["
CDATA_CLOSE = u"]]>"

NEEDS_CDATA = r"[^<>&]*"
NEEDS_ATTR_ESCAPE = u"\"\n\r\\"

def indent(f, times):
    for i in range(times):
        f.write(u"\t")

def attrescape(value):
    value = unicode(value)
    for char in NEEDS_ATTR_ESCAPE:
        value = value.replace(char, u"\\" + char)
    return value

def cdataescape(value):
    if not re.match(NEEDS_CDATA, value):
        return CDATA_OPEN + value + CDATA_CLOSE
    else:
        return value

def opentag(f, name, attrs={}, selfclose=False, newline=True):
    f.write(u"<" + unicode(name))
    if attrs:
        for key, value in attrs.items():
            f.write(unicode(" " + key + '="' + attrescape(value) + '"'))
    nl = u"\n" if newline else u""
    if selfclose:
        f.write(u" />"+nl)
    else:
        f.write(u">"+nl)

def closetag(f, name):
    f.write(u"</" + unicode(name) + u">\n")
    
def writesimple(f, ind, key, value=None, attrs={}):
    indent(f, ind)
    opentag(f, key, attrs, not value, False)
    if value:
        f.write(cdataescape(unicode(value)))
        closetag(f, key)
    else:
        f.write(u"\n")
