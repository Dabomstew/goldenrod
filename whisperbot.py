import config
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import messagequeue
import datetime, time, sys, threading, os.path

class WhisperBot(irc.IRCClient):
    """Connects to twitch chat to carry out dirty whispers."""
    
    nickname = config.botNick
    password = config.botOAuth
    
    def __init__(self, conn, cursor, lock, commandParser):
        self.commandParser = commandParser
        self.isMod = True
        self.messageQueue = None
        self.conn = conn
        self.cursor = cursor
        self.lock = lock
        self.channelMods = []
        
    # db stuff
    def execQueryModify(self, query, args=None):
        try:
            self.lock.acquire(True)
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
            self.lock.release()
    
    def execQuerySelectOne(self, query, args=None):
        try:
            self.lock.acquire(True)
            if(args == None):
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, args)
            return self.cursor.fetchone()
        finally:
            self.lock.release()
        
    def execQuerySelectMultiple(self, query, args=None):
        try:
            self.lock.acquire(True)
            if(args == None):
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, args)
            return self.cursor.fetchall()
        finally:
            self.lock.release()
        
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

    # callbacks for events
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        
        self.messageQueue = messagequeue.MessageQueue(self)
        mqThread = threading.Thread(target=self.messageQueue.run)
        mqThread.daemon = True
        mqThread.start()
        
        self.sendLine("CAP REQ :twitch.tv/commands")
        
        
    def modeChanged(self, user, channel, set, modes, args):
        # do something (change mod status?)
        pass

    def privmsg(self, user, channel, msg):
        # shouldn't be getting privmsgs
        pass
        
    def irc_unknown(self, prefix, command, params):
        if command == "WHISPER":
            user = prefix.split('!', 1)[0]
            msg = params[1].strip()
            reactor.rootLogger.info(("%s --> %s (whisperrecv) : %s" % (user, config.botNick, msg)).decode("utf-8"))
            if msg.startswith(config.cmdChar):
                commandBits = msg[config.cmdCharLen:].split(' ', 1)
                msgCommand = commandBits[0]
                args = ""
                if len(commandBits) == 2:
                    args = commandBits[1]
                self.commandParser.parse(self, user, msgCommand, args, True)
    
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
        self.factory.killBot = True
        self.quit()
        
    def sendWhisper(self, user, message):
        reactor.rootLogger.info(("%s --> %s (whisperqueue) : %s" % (config.botNick, user, message)).decode("utf-8"))
        self.queueMsg("#jtv", "/w %s %s" % (user, message), False)
        
    def addressUser(self, user, message):
        self.sendWhisper(user, message)
    
    def queueMsg(self, channel, message, repeat):
        if repeat:
            self.messageQueue.queueMessageRA(channel, message)
        else:
            self.messageQueue.queueMessage(channel, message)
            
    def isWhisperRequest(self):
        return True
        
    def sendInfoMessage(self, id, user, message):
        self.addressUser(user, message)
    
class WhisperFactory(protocol.ClientFactory):

    def __init__(self, waitTimeout, conn, cursor, lock, commandParser):
        self.killBot = False
        self.oldWait = waitTimeout
        self.timeouts = { 0: 5, 0.1: 5, 5: 10, 10: 30, 30: 60, 60: 300, 300: 300 }
        self.instance = None
        self.conn = conn
        self.cursor = cursor
        self.lock = lock
        self.channel = "_DirectWhisper" # deliberate caps so it never matches a real channel
        self.commandParser = commandParser

    def buildProtocol(self, addr):
        p = WhisperBot(self.conn, self.cursor, self.lock, self.commandParser)
        p.factory = self
        reactor.whisperer = p
        return p

    def clientConnectionLost(self, connector, reason):
        self.instance = None

    def clientConnectionFailed(self, connector, reason):
        self.instance = None