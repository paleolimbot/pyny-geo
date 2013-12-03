'''
Created on Aug 21, 2013

@author: dewey
'''

import serial
from nmea import NmeaSentence, NmeaFilter, NmeaException

class NmeaReceiver(object):
    
    def __init__(self):
        self.serial = None
        self.__nmeaFilter = NmeaFilter()
        self.__open = False
    
    def setNmeaFilter(self, nmeaFilter):
        self.__nmeaFilter = nmeaFilter
    
    def openConnection(self, port, baud=9600, timeout=5):
        if self.serial is not None:
            self.serial.close()
        self.serial = serial.Serial(port)
        self.serial.setTimeout(timeout)
        self.serial.setStopbits(1)
        self.__open = True
    
    def closeConnection(self):
        if self.serial is not None:
            self.serial.close()
        self.__open = False
            
    def isOpen(self):
        return self.__open
    
    def readBuffer(self):
        data = self.serial.read(1) 
        n = self.gpsdevice.inWaiting()
        if n:
            data = data + self.serial.read(n)
        return data
    
    def read(self):
        
        currentLine = ""
        
        while self.isOpen():
            currentLine += self.readBuffer()
            newlineIndex = currentLine.find("\r\n")
            if newlineIndex != -1:
                separateLines = currentLine.split("\r\n")
                if len(separateLines) > 1:
                    currentLine = separateLines[1]
                else:
                    currentLine = ""
                try:
                    sentence = NmeaSentence.parse(separateLines[0])
                    if self.__nmeaFilter.acceptSentence(sentence):
                        self.onNmeaSentenceReceived(sentence)
                except NmeaException, e:
                    self.onNmeaError(e, separateLines[0])
        
    def onNmeaError(self, error, sentenceString):
        print "NmeaException!", sentenceString, error
    
    def onNmeaSentenceReceived(self, sentence):
        print sentence