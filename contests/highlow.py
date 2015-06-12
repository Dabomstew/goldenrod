# shell class

import random
import config
import datetime, time
import math

class Game:

    def __init__(self, contestmanager):
        self.contestmanager = contestmanager
        self.bot = contestmanager.bot
        self.number = 0
        self.guessers = {}
        
    def start(self):
        self.number = random.randint(config.highlowMinNumber, config.highlowMaxNumber)
        print self.number
        msgArgs = (config.highlowMinNumber, config.highlowMaxNumber, config.highlowGuessTimeout, config.highlowPrize, config.currencyPlural, config.contestDurations["highlow"])
        self.bot.channelMsg("High/Low! I have chosen a random number between %d and %d. Have a go at guessing the number in a message and I'll tell you whether your guess was too high or too low. You can guess once every %d seconds. The winner gets %d %s and you have %d seconds. Good luck!" % msgArgs)
        
    def processMessage(self, user, message):
        if message:
            msglow = message.lower()
            timeNow = int(time.time())
            if msglow.startswith("!guess "):
                msglow = msglow[7:]
                
            try:
                numberguess = int(msglow)
                if numberguess < config.highlowMinNumber or numberguess > config.highlowMaxNumber:
                    return
                    
                if "bot" in user:
                    self.bot.channelMsg("%s -> LOL nope." % user)
                    return
                    
                altCheck = self.bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (user,))
                
                if altCheck != None:
                    self.bot.channelMsg("%s -> Known alts aren't allowed to play games." % user)
                    return
                
                if user in self.guessers and self.guessers[user] > timeNow - config.highlowGuessTimeout:
                    self.bot.channelMsg("%s -> Stop spamming guesses." % user)
                    return
                
                self.guessers[user] = timeNow
                if numberguess == self.number:
                    # woo
                    prize = config.highlowPrize
                    emote = random.choice(["Kreygasm", "KevinTurtle", "TriHard"])
                    emotewall = " ".join([emote]*3)
                    self.bot.channelMsg("/me %s | %s guessed %d correctly first! They win %d %s. | %s" % (emotewall, user, self.number, prize, config.currencyPlural, emotewall))
                    userData = self.bot.getUserDetails(user)
                    
                    theirNewBal = userData["balance"] + prize
                    queryArgList = (theirNewBal, user, userData["balance"])
                    self.bot.execQueryModify("UPDATE users SET balance = ?, contests_won = contests_won + 1 WHERE twitchname = ? AND balance = ?", queryArgList)
                    self.bot.updateHighestBalance(userData, theirNewBal)
                    logArgList = (user, "highlow", self.number, prize, timeNow, self.bot.factory.channel)
                    self.bot.execQueryModify("INSERT INTO contestwins (twitchname, gameid, answer, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgList)
                    self.contestmanager.contestIsDone()
                    return
                else:
                    if self.number > numberguess:
                        self.bot.channelMsg("%s -> %d is too low." % (user, numberguess))
                    else:
                        self.bot.channelMsg("%s -> %d is too high." % (user, numberguess))
            except ValueError:
                return
    
    def end(self):
        emote = random.choice(["BibleThump", ":("])
        emotewall = " ".join([emote]*3)
        self.bot.channelMsg("/me %s | No-one guessed correctly, the correct answer was %d. Too bad! | %s" % (emotewall, self.number, emotewall))