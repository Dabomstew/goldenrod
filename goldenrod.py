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
import whisperbot

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
        self.inQuietMode = False
        self.infoSendTimes = {}
        self.quietModeTold = []
        self.shinyMessageTimes = {}
    
    # DB stuff
        
    def execQueryModify(self, query, args=None):
        try:
            lock.acquire(True)
            try:
                if(args == None):
                    self.cursor.execute(query)
                else:
                    self.cursor.execute(query, args)
            except sqlite3.IntegrityError:
                # do nothing because row already exists
                self.conn.commit()
                return 0
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
            self.execQueryModify("INSERT INTO channels (channel, commandsEnabled, quietMode, lastChange) VALUES(?, ?, ?, ?)", (self.factory.channel, False, False, int(time.time())))
            commandInfo = self.execQuerySelectOne("SELECT * FROM channels WHERE channel = ?", (self.factory.channel,))
            
        return commandInfo["commandsEnabled"]
        
    def setCommandsEnabled(self, commandsEnabled):
        self.commandsEnabled = commandsEnabled
        self.execQueryModify("UPDATE channels SET commandsEnabled = ?, lastChange = ? WHERE channel = ?", (commandsEnabled, int(time.time()), self.factory.channel))
        
    def isInQuietMode(self):
        commandInfo = self.execQuerySelectOne("SELECT * FROM channels WHERE channel = ?", (self.factory.channel,))
        if commandInfo == None:
            self.execQueryModify("INSERT INTO channels (channel, commandsEnabled, quietMode, lastChange) VALUES(?, ?, ?, ?)", (self.factory.channel, False, False, int(time.time())))
            commandInfo = self.execQuerySelectOne("SELECT * FROM channels WHERE channel = ?", (self.factory.channel,))
            
        return commandInfo["quietMode"]
        
    def setQuietMode(self, quietMode):
        self.inQuietMode = quietMode
        self.execQueryModify("UPDATE channels SET quietMode = ?, lastChange = ? WHERE channel = ?", (quietMode, int(time.time()), self.factory.channel))
        self.quietModeTold = []
            
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
        self.sendLine("CAP REQ :twitch.tv/commands")
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
        self.inQuietMode = self.isInQuietMode()
        self.quietModeTold = []
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
            
        # Check to see if it is a potential command
        msg = msg.strip()
        if (self.commandsEnabled or (user == self.factory.channel or user == config.botOwner or user in self.channelMods)) and self.acceptCommands:
            if not self.commandsEnabled and (user == self.factory.channel or user in self.channelMods) and user != config.botOwner:
                if not msg.startswith("%sgoldenrodctl" % config.cmdChar):
                    return
            timeNow = int(time.time())
            if (user not in self.shinyMessageTimes) or self.shinyMessageTimes[user] <= timeNow - 60:
                self.shinyMessageTimes[user] = timeNow
                if random.randint(1, 8192) == 6969:
                    self.channelMsg("/me *** %s's MESSAGE WAS SHINIED! THEY WIN %d %s. ***" % (user.upper(), config.shinyPrize, config.currencyPlural.upper()))
                    userData = self.getUserDetails(user)
                    self.execQueryModify("INSERT INTO shinies (twitchname, reward, whenHappened, channel) VALUES(?, ?, ?, ?)", (user, config.shinyPrize, int(time.time()), self.factory.channel))
                    self.execQueryModify("UPDATE users SET balance = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", (userData["balance"]+config.shinyPrize, int(time.time()), user, userData["balance"]))
                    if user == self.factory.channel:
                        self.channelMsg("/me Strimmer got a shiny? DansGame R I G G E D DansGame")
                    
                    if user == config.botOwner:
                        self.channelMsg("/me The owner got a shiny? DansGame DansGame DansGame 1 0 0 % R I G G E D DansGame DansGame DansGame")
            
            if self.contestManager.currentContest != None:
                self.contestManager.currentContest.processMessage(user, msg)
            if msg.startswith(config.cmdChar):
                commandBits = msg[config.cmdCharLen:].split(' ', 1)
                command = commandBits[0]
                args = ""
                if len(commandBits) == 2:
                    args = commandBits[1]
                self.commandParser.parse(self, user, command, args, False)
                
    def noticed(self, user, channel, msg):
        reactor.rootLogger.info(("%s --> (notice) %s : %s" % (user, channel, msg)).decode("utf-8"))
        
        # Check to see if they're sending me a private message
        if user == "tmi.twitch.tv" and msg.startswith(config.twitchModsMsg):
            self.channelMods = msg[len(config.twitchModsMsg):].split(", ")
            self.isMod = (self.nickname in self.channelMods) or (self.nickname == self.factory.channel)
    
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
            
    def addressUser(self, user, message):
        if self.inQuietMode:
            reactor.whisperer.sendWhisper(user, message)
        else:
            self.channelMsg("%s -> %s" % (user, message))
        
    def isWhisperRequest(self):
        return False
        
    def sendInfoMessage(self, id, user, message):
        if self.inQuietMode:
            reactor.whisperer.sendWhisper(user, message)
        else:
            isMod = (user in self.channelMods) or user == self.factory.channel or user == config.botOwner
            timeNow = int(time.time())
            if isMod or (id not in self.infoSendTimes) or self.infoSendTimes[id] <= timeNow - 60:
                self.infoSendTimes[id] = timeNow
                self.channelMsg(message)
            
    def tellAboutQuietMode(self, user):
        if user not in self.quietModeTold:
            self.quietModeTold.append(user)
            reactor.whisperer.sendWhisper(user, "This stream is currently in quiet mode, spammy commands like !handout are turned off. Please respect the streamer's wishes and keep the spam low.")
        
        
def connectToTwitch(startChannel, commandParser, waitTimeout):
    if waitTimeout > 0:
        time.sleep(waitTimeout)
    f = GoldenrodFactory(startChannel, commandParser, waitTimeout)
    # connect factory to this host and port
    twitchServers = ["192.16.64.11", "192.16.64.144", "192.16.64.145", "192.16.64.146", "192.16.64.152", "192.16.64.155"]
    myServer = random.choice(twitchServers)
    reactor.connectTCP(myServer, 6667, f)
    
def connectWhisperer(commandParser, waitTimeout):
    if waitTimeout > 0:
        time.sleep(waitTimeout)
    f = whisperbot.WhisperFactory(waitTimeout, conn, cursor, lock, commandParser)
    # connect factory to this host and port
    twitchGroupServers = ["199.9.253.120"]
    myServer = random.choice(twitchGroupServers)
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
    connectWhisperer(commandParser, 0)

    # setup channel manager
    channelManager = channelmanager.ChannelManager(conn, cursor, lock, channelInstances)
    cmThread = threading.Thread(target=channelManager.run)
    cmThread.daemon = True
    cmThread.start()
    
    # run bot
    reactor.run()