# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
import logging

# system imports

import datetime, time, sys, threading, os.path
import commandparser
import messagequeue
import contestmanager
import config
import random
import sqlite3
import channelmanager

commandParser = None
channelManager = None
channelInstances = {}
allInstances = []
conn = sqlite3.connect("goldenrod.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
try:
    cursor.execute("SELECT * FROM slotspool")
    cursor.fetchone()
except sqlite3.OperationalError:
    import dbcreator
    dbcreator.create(conn, cursor)

if os.path.isfile("./contests.db"):
    # attach it
    cursor.execute("ATTACH DATABASE \"contests.db\" AS contests")
    
lock = threading.Lock()

class GoldenrodNostalgiaB(irc.IRCClient):
    """A gambling IRC bot."""
    
    nickname = config.botNick
    password = config.botOAuth
    
    def __init__(self, commandParser):
        self.commandParser = commandParser
        self.acceptCommands = False
        self.isMod = False
        self.channelMods = []
        self.messageQueue = None
        self.lurklessCount = 0
        self.conn = conn
        self.cursor = cursor
        self.contestManager = None
        self.commandsEnabled = False
        self.contestsEnabled = False
    
    # DB stuff
        
    def execQueryModify(self, query, args=None):
        try:
            lock.acquire(True)
            if(args == None):
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, args)
            rowc = self.cursor.rowcount
            self.conn.commit()
            return rowc
        finally:
            lock.release()
    
    def execQuerySelectOne(self, query, args=None):
        try:
            lock.acquire(True)
            if(args == None):
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, args)
            return self.cursor.fetchone()
        finally:
            lock.release()
        
    def execQuerySelectMultiple(self, query, args=None):
        try:
            lock.acquire(True)
            if(args == None):
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, args)
            return self.cursor.fetchall()
        finally:
            lock.release()
        
    def getUserDetails(self, user):
        userData = self.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (user,))
        if userData == None:
            self.createNewUser(user)
            return self.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (user,))
        else:
            self.execQueryModify("UPDATE users SET last_activity = ? WHERE twitchname = ?", (int(time.time()), user))
            return userData
    
    def createNewUser(self, user):
        self.execQueryModify("INSERT INTO users (twitchname, balance, last_activity, highest_balance) VALUES(?, ?, ?, ?)", (user, config.startingBalance, int(time.time()), config.startingBalance))
        
    def updateHighestBalance(self, userData, newBalance):
        if newBalance > userData["highest_balance"]:
            self.execQueryModify("UPDATE users SET highest_balance = ? WHERE twitchname = ?", (newBalance, userData["twitchname"]))
            
    def commandsAreEnabled(self):
        commandInfo = self.execQuerySelectOne("SELECT * FROM channels WHERE channel = ?", (self.factory.channel,))
        if commandInfo == None:
            self.execQueryModify("INSERT INTO channels (channel, commandsEnabled, lastChange) VALUES(?, ?, ?)", (self.factory.channel, False, int(time.time())))
            commandInfo = self.execQuerySelectOne("SELECT * FROM channels WHERE channel = ?", (self.factory.channel,))
            
        return commandInfo["commandsEnabled"]
        
    def setCommandsEnabled(self, commandsEnabled):
        self.commandsEnabled = commandsEnabled
        self.execQueryModify("UPDATE channels SET commandsEnabled = ?, lastChange = ? WHERE channel = ?", (commandsEnabled, int(time.time()), self.factory.channel))
            
    # return 0 if they can play or cooldown in seconds remaining otherwise
    def canPlayGame(self, userData):
        if(userData["last_game"] == None):
            return 0
        currTimestamp = int(time.time())
        if(currTimestamp - userData["last_game"] >= config.gameCooldown):
            return 0
        else:
            return config.gameCooldown - (currTimestamp - userData["last_game"])

    # callbacks for events
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
        self.acceptCommands = False
        self.isMod = (config.botNick == self.factory.channel)
        self.channelMods = []
        self.contestsEnabled = False
        
        self.messageQueue = messagequeue.MessageQueue(self)
        mqThread = threading.Thread(target=self.messageQueue.run)
        mqThread.daemon = True
        mqThread.start()
        
        self.contestManager = contestmanager.ContestManager(self)
        cmThread = threading.Thread(target=self.contestManager.run)
        cmThread.daemon = True
        cmThread.start()

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.commandsEnabled = self.commandsAreEnabled()
        self.acceptCommands = True
        self.isMod = (config.botNick == self.factory.channel)
        self.channelMods = []
        self.channelMsg(".mods")
        if config.doSayHello and self.commandsEnabled:
            self.channelMsg(config.helloMessage)
        
        
    def modeChanged(self, user, channel, set, modes, args):
        # do something (change mod status?)
        pass

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        reactor.rootLogger.info(("%s --> %s : %s" % (user, channel, msg)).decode("utf-8"))
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            if user == "jtv":
                if msg.startswith(config.twitchModsMsg):
                    self.channelMods = msg[len(config.twitchModsMsg):].split(", ")
                    self.isMod = (self.nickname in self.channelMods) or (self.nickname == self.factory.channel)
                    
            return
            
        # Otherwise check to see if it is a potential command
        if (self.commandsEnabled or (user == self.factory.channel or user == config.botOwner)) and self.acceptCommands:
            if not self.commandsEnabled and user == self.factory.channel and user != config.botOwner:
                if not msg.startswith("%sgoldenrodctl" % config.cmdChar):
                    return
            if self.contestManager.currentContest != None:
                self.contestManager.currentContest.processMessage(user, msg)
            if msg.startswith(config.cmdChar):
                commandBits = msg[config.cmdCharLen:].split(' ', 1)
                command = commandBits[0]
                args = ""
                if len(commandBits) == 2:
                    args = commandBits[1]
                self.commandParser.parse(self, user, command, args)
    
    def leaveChannel(self, byeMessage):
        if not self.acceptCommands:
            return
        if byeMessage != None and byeMessage != "":
            self.queueMsg("#%s" % self.factory.channel, byeMessage, True)
        self.acceptCommands = False
        klThread = threading.Thread(target=self.killRequest)
        klThread.daemon = True
        klThread.start()
    
    def killRequest(self):
        try:
            while not (self.messageQueue == None) and not self.messageQueue.queue.empty():
                time.sleep(0.5)
        except AttributeError:
            pass
        from goldenrod import allInstances
        allInstances.remove(self)
        self.factory.killBot = True
        self.quit()
    
    def channelMsg(self, message):
        reactor.rootLogger.info(("%s --> %s (queueing) : %s" % (config.botNick, "#%s"%self.factory.channel, message)).decode("utf-8"))
        self.queueMsg("#%s" % self.factory.channel, message, False)
        
    def channelMsgRA(self, message):
        reactor.rootLogger.info(("%s --> %s (queueing, repeat) : %s" % (config.botNick, "#%s"%self.factory.channel, message)).decode("utf-8"))
        self.queueMsg("#%s" % self.factory.channel, message, True)
        
    def queueMsg(self, channel, message, repeat):
        if repeat:
            self.messageQueue.queueMessageRA(channel, message)
        else:
            self.messageQueue.queueMessage(channel, message)
        
def connectToTwitch(startChannel, commandParser, waitTimeout):
    if waitTimeout > 0:
        time.sleep(waitTimeout)
    f = GoldenrodFactory(startChannel, commandParser, waitTimeout)
    # connect factory to this host and port
    twitchServers = ["192.16.64.11", "192.16.64.144", "192.16.64.145", "192.16.64.146", "192.16.64.152", "192.16.64.155"]
    myServer = random.choice(twitchServers)
    reactor.connectTCP(myServer, 6667, f)
    
class GoldenrodFactory(protocol.ClientFactory):

    def __init__(self, channel, commandParser, waitTimeout):
        self.channel = channel
        self.killBot = False
        self.oldWait = waitTimeout
        self.timeouts = { 0: 5, 0.1: 5, 5: 10, 10: 30, 30: 60, 60: 300, 300: 300 }
        self.commandParser = commandParser
        self.instance = None

    def buildProtocol(self, addr):
        from goldenrod import channelInstances, allInstances
        if self.channel in channelInstances:
            self.instance = None
            return None
        p = GoldenrodNostalgiaB(self.commandParser)
        channelInstances[self.channel] = p
        allInstances.append(p)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        from goldenrod import channelInstances, allInstances
        if self.instance in channelInstances.values():
            channelInstances.remove(self.instance)
        if self.instance in allInstances:
            allInstances.remove(self.instance) 
        self.instance = None

    def clientConnectionFailed(self, connector, reason):
        from goldenrod import channelInstances, allInstances
        if self.instance in channelInstances.values():
            channelInstances.remove(self.instance)
        if self.instance in allInstances:
            allInstances.remove(self.instance)    
        self.instance = None
            
def joinNewChannel(channel):
    from goldenrod import channelInstances
    if channel.startswith("#"):
        channel = channel[1:]
    if channel in channelInstances:
        return
    connectToTwitch(channel, reactor.commandParser, 0)

def leaveChannel(channel, message):
    from goldenrod import channelInstances
    if channel.startswith("#"):
        channel = channel[1:]
    if channel not in channelInstances:
        return
    channelInstances[channel].leaveChannel(message)
    del channelInstances[channel]

def commandsAreEnabled(channel):
    if channel.startswith("#"):
        channel = channel[1:]
    try:
        lock.acquire(True)
        cursor.execute("SELECT * FROM channels WHERE channel = ?", (channel,))
        channelData = cursor.fetchone()
        if channelData == None:
            return False
        else:
            return channelData["commandsEnabled"]
    finally:
        lock.release()

def addToCommandsEnabled(channel):
    from goldenrod import channelInstances
    if channel.startswith("#"):
        channel = channel[1:]
    if channel not in channelInstances:
        try:
            lock.acquire(True)
            cursor.execute("SELECT * FROM channels WHERE channel = ?", (channel,))
            channelData = cursor.fetchone()
            if channelData == None:
                cursor.execute("INSERT INTO channels (channel, commandsEnabled, lastChange) VALUES(?, ?, ?)", (channel, True, int(time.time())))
            else:
                cursor.execute("UPDATE channels SET commandsEnabled = ?, lastChange = ? WHERE channel = ?", (True, int(time.time()), channel))
            return
        finally:
            lock.release()
    else:
        channelInstances[channel].setCommandsEnabled(True)

def removeFromCommandsEnabled(channel):
    from goldenrod import channelInstances
    if channel.startswith("#"):
        channel = channel[1:]
    if channel not in channelInstances:
        try:
            lock.acquire(True)
            cursor.execute("SELECT * FROM channels WHERE channel = ?", (channel,))
            channelData = cursor.fetchone()
            if channelData == None:
                cursor.execute("INSERT INTO channels (channel, commandsEnabled, lastChange) VALUES(?, ?, ?)", (channel, False, int(time.time())))
            else:
                cursor.execute("UPDATE channels SET commandsEnabled = ?, lastChange = ? WHERE channel = ?", (False, int(time.time()), channel))
            return
        finally:
            lock.release()
    else:
        channelInstances[channel].setCommandsEnabled(False)

if __name__ == '__main__':
    #initialize logging
    #log.startLogging(sys.stdout)
    log.startLogging(open('./logs/%d_stdouterr.log' % (time.time()), 'w'))
    
    handler = logging.FileHandler('./logs/%d_messages.log' % (time.time()), "w",
                                  encoding = "UTF-8")
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    reactor.rootLogger = root_logger
    
    commandParser = commandparser.CommandParser()
    commandParser.loadCommands()
    reactor.commandParser = commandParser
    
    connectToTwitch(config.botNick, commandParser, 0)

    # setup channel manager
    channelManager = channelmanager.ChannelManager(conn, cursor, lock, channelInstances)
    cmThread = threading.Thread(target=channelManager.run)
    cmThread.daemon = True
    cmThread.start()
    
    # run bot
    reactor.run()