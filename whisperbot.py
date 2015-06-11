import config
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import messagequeue
import datetime, time, sys, threading, os.path

class WhisperBot(irc.IRCClient):
    """Connects to twitch chat to carry out dirty whispers."""
    
    nickname = config.botNick
    password = config.botOAuth
    
    def __init__(self, conn, cursor, lock):
        self.isMod = True
        self.messageQueue = None
        self.conn = conn
        self.cursor = cursor
        self.lock = lock
        
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
            args = params[1].strip().lower()
            if args.startswith("!balance"):
                args = args[8:].strip()
                if not args:
                    self.sendWhisper(user, "Your balance is %d %s." % (self.getUserDetails(user)["balance"], config.currencyPlural))
                else:
                    arglist = args.split()
                    balanceCheck = self.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (arglist[0].lower(),))
                    if balanceCheck == None:
                        self.sendWhisper(user, "Your balance is %d %s." % (self.getUserDetails(user)["balance"], config.currencyPlural))
                    else:
                        self.sendWhisper(user, ("%s's balance is %d %s." % (balanceCheck["twitchname"], balanceCheck["balance"], config.currencyPlural)).encode("utf-8"))
    
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
        reactor.rootLogger.info(("%s --> %s (whisper) : %s" % (config.botNick, user, message)).decode("utf-8"))
        self.queueMsg("#jtv", "/w %s %s" % (user, message), False)
        
    def queueMsg(self, channel, message, repeat):
        if repeat:
            self.messageQueue.queueMessageRA(channel, message)
        else:
            self.messageQueue.queueMessage(channel, message)
    
class WhisperFactory(protocol.ClientFactory):

    def __init__(self, waitTimeout, conn, cursor, lock):
        self.killBot = False
        self.oldWait = waitTimeout
        self.timeouts = { 0: 5, 0.1: 5, 5: 10, 10: 30, 30: 60, 60: 300, 300: 300 }
        self.instance = None
        self.conn = conn
        self.cursor = cursor
        self.lock = lock

    def buildProtocol(self, addr):
        p = WhisperBot(self.conn, self.cursor, self.lock)
        p.factory = self
        reactor.whisperer = p
        return p

    def clientConnectionLost(self, connector, reason):
        self.instance = None

    def clientConnectionFailed(self, connector, reason):
        self.instance = None