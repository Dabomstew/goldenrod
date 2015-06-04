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
        
    def presentNumber(self, number, maxNumber):
        digits = len(str(maxNumber))
        return ("%0"+str(digits)+"d") % number
        
    def checkMatches(self, number, target, maxNumber):
        digits = len(str(maxNumber))
        matches = 0
        for digit in xrange(0, digits):
            if (number / (10 ** digit)) % 10 == (target / (10 ** digit)) % 10:
                matches += 1
        return matches
        
    def start(self):
        self.number = random.randint(config.lotteryMinNumber, config.lotteryMaxNumber)
        print self.number
        msgArgs = (self.presentNumber(config.lotteryMinNumber, config.lotteryMaxNumber), self.presentNumber(config.lotteryMaxNumber, config.lotteryMaxNumber), config.lotteryGuessTimeout, config.lotteryPrize, config.currencyPlural, config.contestDuration)
        self.bot.channelMsg("Goldenrod Lottery! I have chosen a random trainer ID between %s and %s. Have a go at guessing the number in a message and I'll tell you how many digits from your guess match the digit in the same position in the answer. You can guess once every %d seconds. The winner gets %d %s and you have %d seconds. Good luck!" % msgArgs)
        
    def processMessage(self, user, message):
        if message:
            msglow = message.lower()
            timeNow = int(time.time())
            if msglow.startswith("!guess "):
                msglow = msglow[7:]
                
            try:
                numberguess = int(msglow)
                if numberguess < config.lotteryMinNumber or numberguess > config.lotteryMaxNumber:
                    return
                
                if user in self.guessers and self.guessers[user] > timeNow - config.lotteryGuessTimeout:
                    self.bot.channelMsg("%s -> Stop spamming guesses." % user)
                    return
                
                self.guessers[user] = timeNow
                if numberguess == self.number:
                    # woo
                    prize = config.lotteryPrize
                    emote = random.choice(["Kreygasm", "KevinTurtle", "TriHard"])
                    emotewall = " ".join([emote]*3)
                    self.bot.channelMsg("/me %s | %s guessed %s correctly first! They win %d %s. | %s" % (emotewall, user, self.presentNumber(self.number, config.lotteryMaxNumber), prize, config.currencyPlural, emotewall))
                    userData = self.bot.getUserDetails(user)
                    
                    theirNewBal = userData["balance"] + prize
                    queryArgList = (theirNewBal, user, userData["balance"])
                    self.bot.execQueryModify("UPDATE users SET balance = ?, contests_won = contests_won + 1 WHERE twitchname = ? AND balance = ?", queryArgList)
                    self.bot.updateHighestBalance(userData, theirNewBal)
                    logArgList = (user, "luckylottery", self.presentNumber(self.number, config.lotteryMaxNumber), prize, timeNow, self.bot.factory.channel)
                    self.bot.execQueryModify("INSERT INTO contestwins (twitchname, gameid, answer, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgList)
                    self.contestmanager.contestIsDone()
                    return
                else:
                    numbersCorrect = self.checkMatches(numberguess, self.number, config.lotteryMaxNumber)
                    msgargs = (user, self.presentNumber(numberguess, config.lotteryMaxNumber), numbersCorrect)
                    self.bot.channelMsg("%s -> %s has %d correct digits in the right positions." % msgargs)
            except ValueError:
                return
    
    def end(self):
        emote = random.choice(["BibleThump", ":("])
        emotewall = " ".join([emote]*3)
        self.bot.channelMsg("/me %s | No-one guessed correctly, the correct answer was %s. Too bad! | %s" % (emotewall, self.presentNumber(self.number, config.lotteryMaxNumber), emotewall))