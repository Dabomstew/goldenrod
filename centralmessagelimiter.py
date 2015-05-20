import Queue
import time, sys, threading

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

centralRateLimit = 95
centralRatePeriod = 30

class CentralMessageLimiter:

    def __init__(self):
        self.oldMessageTimes = [0] * (centralRateLimit + 5)
        self.messagesSent = 0
        self.mqLock = threading.Lock()
    
    def run(self):
        while True:
            time.sleep(0.1)
            self.clearOldMessageTimes()
    
    def reserveMessage(self):
        with self.mqLock:
            if self.messagesSent >= centralRateLimit:
                return {"response": False, "wait": centralRatePeriod - (time.time() - self.oldMessageTimes[0])}
            else:
                self.oldMessageTimes[self.messagesSent] = time.time()
                self.messagesSent += 1
                return {"response": True}
    
    def clearOldMessageTimes(self):
        with self.mqLock:
            clearTime = time.time()
            msgsCleared = 0
            while(self.oldMessageTimes[0] + centralRatePeriod <= clearTime and self.oldMessageTimes[0] != 0):
                self.oldMessageTimes = self.oldMessageTimes[1:]
                self.oldMessageTimes.append(0)
                self.messagesSent -= 1
                msgsCleared += 1
        