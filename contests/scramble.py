# shell class

import random
import config
import datetime, time
import math

class Game:

    def __init__(self, contestmanager):
        self.contestmanager = contestmanager
        self.bot = contestmanager.bot
        self.word = ""
        self.scrambledWord = ""
        self.startTime = 0
    
    def canBeScrambled(self, word):
        if len(word) < 3:
            return False
        if " " in word:
            return False
        
        chars = []
        for i in xrange(0, len(word)):
            if word[i] not in chars:
                chars.append(word[i])
                
        if word[0] == word[len(word)-1]:
            return len(chars) > 2
        else:
            return len(chars) > 1
            
    def shuffleWord(self, word):
        shuffledWord = word
        wordlen = len(word)
        while shuffledWord[0] == word[0] or shuffledWord[wordlen-1] == word[wordlen-1]:
            wordL = list(word)
            random.shuffle(wordL)
            shuffledWord = ''.join(wordL)
        
        return shuffledWord.upper()
        
    def calcPrize(self, word, elapsedTime):
        prize = config.scramblePrizeBase
        
        if len(word) < 8:
            prize = int(prize * math.pow(0.8, 8-len(word)))
        elif len(word) > 10:
            prize = int(prize * math.pow(1.05, len(word)-10))
            
        if elapsedTime >= config.scramblePrizeReducFirst:
            prize = int(prize/2)
            
        if elapsedTime >= config.scramblePrizeReducSecond:
            prize = int(prize/2)  
            
        return prize
        
        
    def start(self):
        # first select a word
        self.startTime = int(time.time())
        self.word = ""
        while not self.canBeScrambled(self.word):
            wordData = self.bot.execQuerySelectOne("SELECT * FROM hangman_words WHERE used_in_cycle = 0 AND length(word) >= 5 ORDER BY RANDOM() LIMIT 1")
            if wordData == None:
                # no questions left
                self.bot.execQueryModify("UPDATE hangman_words SET used_in_cycle = 0 WHERE length(word) >= 5")
                wordData = self.bot.execQuerySelectOne("SELECT * FROM hangman_words WHERE used_in_cycle = 0 AND length(word) >= 5 ORDER BY RANDOM() LIMIT 1")
            self.bot.execQueryModify("UPDATE hangman_words SET used_in_cycle = 1 WHERE id = ?", (wordData["id"],))
            self.word = wordData["word"].encode("utf-8").lower()
        print self.word
        self.scrambledWord = self.shuffleWord(self.word)
        msgArgs = (self.calcPrize(self.word, 0), config.currencyPlural, config.contestDurations["scramble"])
        self.bot.channelMsg("Word scramble! I have chosen a random word from my collection of Pokemon and Pokemon speedrunning-related terms and scrambled it. The first person to guess this word gets %d %s, with some taken off if it takes too long (to discourage cheating). You have %d seconds. Good luck!" % msgArgs)
        self.bot.channelMsg("Kappa Kappa Kappa | The word is: %s | Kappa Kappa Kappa" % self.scrambledWord)
        
    def processMessage(self, user, message):
        if message == None:
            initialmsg = ""
        else:
            initialmsg = message.strip().lower()
        
        guessme = "%sguess" % config.cmdChar
        if initialmsg:
            if len(initialmsg) == len(self.word) and not message.strip().startswith(config.cmdChar):
                initialmsg = "%s %s" % (guessme,message)
                
            arglist = initialmsg.strip().split()
            if len(arglist) >= 2 and arglist[0].lower() == guessme:
                if "bot" in user:
                    self.bot.channelMsg("%s -> LOL nope." % user)
                    return
                    
                altCheck = self.bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (user,))
                
                if altCheck != None:
                    self.bot.channelMsg("%s -> Known alts aren't allowed to play games." % user)
                    return
                                
                if(len(arglist[1]) == len(self.word)):
                    lowerword = arglist[1].lower()
                    if(lowerword == self.word):
                        # woo they won
                        elapsedTime = int(time.time()) - self.startTime
                        prize = self.calcPrize(self.word, elapsedTime)
                        
                        emote = random.choice(["Kreygasm", "KevinTurtle", "TriHard"])
                        emotewall = " ".join([emote]*3)
                        
                        self.bot.channelMsg("/me %s | %s guessed %s correctly first! They win %d %s. | %s" % (emotewall, user, self.word, prize, config.currencyPlural, emotewall))
                        userData = self.bot.getUserDetails(user)
                        
                        theirNewBal = userData["balance"] + prize
                        queryArgList = (theirNewBal, user, userData["balance"])
                        self.bot.execQueryModify("UPDATE users SET balance = ?, contests_won = contests_won + 1 WHERE twitchname = ? AND balance = ?", queryArgList)
                        self.bot.updateHighestBalance(userData, theirNewBal)
                        logArgList = (user, "scramble", self.word, prize, int(time.time()), self.bot.factory.channel)
                        self.bot.execQueryModify("INSERT INTO contestwins (twitchname, gameid, answer, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgList)
                        self.contestmanager.contestIsDone()
                        return
                    
    
    def end(self):
        emote = random.choice(["BibleThump", ":("])
        emotewall = " ".join([emote]*3)
        self.bot.channelMsg("/me %s | No-one guessed correctly, the correct answer was %s. Too bad! | %s" % (emotewall, self.word, emotewall))
