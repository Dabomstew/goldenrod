import Queue
import time, sys, threading

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

twitchRepeatTimeout = 30
twitchDelayMod = 0.05
twitchDelayNonMod = 1.7
twitchRateLimitMod = 90
twitchRateLimitNonMod = 15
twitchRateLimitPeriod = 30

class MessageQueue:

    def __init__(self, bot):
        self.bot = bot
        self.queue = Queue.Queue()
        self.lastMessage = ""
        self.lastMessageTime = 0
        self.oldMessageTimes = [0] * 100
        self.messagesSent = 0
    
    def run(self):
        while True:
            message = self.queue.get()
            delay = twitchDelayMod if self.bot.isMod else twitchDelayNonMod
            timeNow = time.time()
            if message["message"].strip() == self.lastMessage and not message["repeat"] and timeNow - twitchRepeatTimeout < self.lastMessageTime:
                # drop for being a repeat
                continue
            else:
                earliestSendTime = self.lastMessageTime + delay
                if timeNow < earliestSendTime:
                    time.sleep(earliestSendTime - timeNow)
                self.clearOldMessageTimes()
                rateLimit = twitchRateLimitMod if self.bot.isMod else twitchRateLimitNonMod
                while(self.messagesSent >= rateLimit):
                    time.sleep(0.5)
                    self.clearOldMessageTimes()
                if message["message"].lower().startswith("/me "):
                    message["message"] = message["message"][4:]
                    reactor.callFromThread(self.bot.describe, message["channel"], message["message"])
                else:
                    reactor.callFromThread(self.bot.msg, message["channel"], message["message"], 1024)
                self.lastMessageTime = time.time()
                self.lastMessage = message["message"].strip()
                self.oldMessageTimes[self.messagesSent] = self.lastMessageTime
                self.messagesSent += 1
                
    def queueMessage(self, channel, message):
        self.queue.put({"channel": channel, "message": message, "repeat": False})
    
    def queueMessageRA(self, channel, message):
        self.queue.put({"channel": channel, "message": message, "repeat": True})
    
    def clearOldMessageTimes(self):
        clearTime = time.time()
        msgsCleared = 0
        while(self.oldMessageTimes[0] + twitchRateLimitPeriod <= clearTime and self.oldMessageTimes[0] != 0):
            self.oldMessageTimes = self.oldMessageTimes[1:]
            self.oldMessageTimes.append(0)
            self.messagesSent -= 1
            msgsCleared += 1
            
        