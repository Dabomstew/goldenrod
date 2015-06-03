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
        self.guesses = []
        
    def start(self):
        self.number = random.randint(config.guessMinNumber, config.guessMaxNumber)
        print self.number
        msgArgs = (config.guessMinNumber, config.guessMaxNumber, config.guessPrize, config.currencyPlural, config.contestDuration)
        self.bot.channelMsg("Guess The Number! I have chosen a random number between %d and %d. Put in your guess with !guess number. If you guess correctly you win %d %s and if no-one guesses correctly the closest gets a consolation prize. You have %d seconds. Good luck!" % msgArgs)
        
    def processMessage(self, user, message):
        if message:
            arglist = message.split()
            if len(arglist) >= 2 and arglist[0].lower() == "!guess":
                try:
                    guessNum = int(arglist[1])
                except ValueError:
                    return
                oldGuess = None
                for guess in self.guesses:
                    if guess[0] == user:
                        oldGuess = guess
                        break
                
                if oldGuess != None:
                    self.guesses.remove(oldGuess)
                
                newGuess = [user, guessNum, time.time()]
                self.guesses.append(newGuess)
    
    def end(self):
        emote = random.choice(["Kreygasm", "KevinTurtle", "TriHard"])
        emotewall = " ".join([emote]*3)
        for guess in self.guesses:
            if guess[1] == self.number:
                self.bot.channelMsg("/me %s | %s guessed %d correctly first! They win %d %s. | %s" % (emotewall, guess[0], guess[1], config.guessPrize, config.currencyPlural, emotewall))
                userData = self.bot.getUserDetails(guess[0])
                theirNewBal = userData["balance"] + config.guessPrize
                queryArgList = (theirNewBal, guess[0], userData["balance"])
                self.bot.execQueryModify("UPDATE users SET balance = ?, contests_won = contests_won + 1 WHERE twitchname = ? AND balance = ?", queryArgList)
                self.bot.updateHighestBalance(userData, theirNewBal)
                logArgList = (guess[0], "guessnumber", self.number, config.guessPrize, int(time.time()), self.bot.factory.channel)
                self.bot.execQueryModify("INSERT INTO contestwins (twitchname, gameid, answer, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgList)
                return
        self.bot.channelMsg("No-one guessed correctly, the correct answer was %d. Too bad! Let's see who was closest..." % self.number)
        closestScore = 99999999
        for guess in self.guesses:
            closestScore = min(closestScore, abs(self.number - guess[1]))
        
        if closestScore != 99999999:
            for guess in self.guesses:
                if abs(self.number - guess[1]) == closestScore:
                    self.bot.channelMsg("/me %s | %s's guess of %d was the closest. They win the consolation prize of %d %s. | %s" % (emotewall, guess[0], guess[1], config.guessPrizeConsolation, config.currencyPlural, emotewall))
                    userData = self.bot.getUserDetails(guess[0])
                    theirNewBal = userData["balance"] + config.guessPrizeConsolation
                    queryArgList = (theirNewBal, guess[0], userData["balance"])
                    self.bot.execQueryModify("UPDATE users SET balance = ?, contests_won = contests_won + 1 WHERE twitchname = ? AND balance = ?", queryArgList)
                    self.bot.updateHighestBalance(userData, theirNewBal)
                    logArgList = (guess[0], "guessnumber", "%d for %d" % (guess[1], self.number), config.guessPrizeConsolation, int(time.time()), self.bot.factory.channel)
                    self.bot.execQueryModify("INSERT INTO contestwins (twitchname, gameid, answer, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgList)
                    return