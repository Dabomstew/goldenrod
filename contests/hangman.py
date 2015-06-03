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
        self.guessedLetters = []
        self.fullGuesses = []
        
    def printWord(self):
        result = []
        for i in xrange(0, len(self.word)):
            if i > 0:
                result.append(' ')
            if self.word[i] in self.guessedLetters:
                result.append(self.word[i])
            else:
                result.append('_')
                
        self.bot.channelMsg(''.join(result).upper())
        
    def start(self):
        # first select a word
        wordData = self.bot.execQuerySelectOne("SELECT * FROM hangman_words WHERE used_in_cycle = 0 ORDER BY RANDOM() LIMIT 1")
        if wordData == None:
            # no questions left
            self.bot.execQueryModify("UPDATE hangman_words SET used_in_cycle = 0")
            wordData = self.bot.execQuerySelectOne("SELECT * FROM hangman_words WHERE used_in_cycle = 0 ORDER BY RANDOM() LIMIT 1")
        self.bot.execQueryModify("UPDATE hangman_words SET used_in_cycle = 1 WHERE id = ?", (wordData["id"],))
        self.word = wordData["word"].encode("utf-8").lower()
        print self.word
        msgArgs = (config.hangmanPrizeBase, config.currencyPlural, config.hangmanPrizeLetterReduction, config.contestDuration)
        self.bot.channelMsg("Hangman! I have chosen a random word from my collection of Pokemon and Pokemon speedrunning-related terms and the first person to guess the word gets %d %s, minus %d for each unique letter guessed before the successful guess. You can guess either a single letter (e.g. !guess a) or an answer (e.g. !guess bulbasaur), both with !guess. You only get one guess at the full word, but you'll be let off if your guess isn't the right length or doesn't match the letters revealed so far. You have %d seconds. Good luck!" % msgArgs)
        self.printWord()
        
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
                if(len(arglist[1]) == 1):
                    argchar = arglist[1].lower()[0]
                    if argchar >= 'a' and argchar <= 'z':
                        if argchar not in self.guessedLetters:
                            self.guessedLetters.append(argchar)
                            if argchar in self.word:
                                self.printWord()
                            allRevealed = True
                            for i in xrange(0, len(self.word)):
                                if self.word[i] not in self.guessedLetters:
                                    allRevealed = False
                            
                            if allRevealed:
                                emote = random.choice(["BibleThump"], ":(")
                                emotewall = " ".join([emote]*3)
                                self.bot.channelMsg("/me %s | Sorry everyone, the whole word got revealed before anyone guessed it. Better luck next time! | %s" % (emotewall, emotewall))
                                self.contestmanager.contestIsDone()
                                return
                                
                if(len(arglist[1]) == len(self.word)):
                    if user in self.fullGuesses:
                        # banned already
                        return
                    lowerword = arglist[1].lower()
                    if(lowerword == self.word):
                        # woo they won
                        prize = config.hangmanPrizeBase - len(self.guessedLetters)*config.hangmanPrizeLetterReduction
                        if prize <= 0:
                            prize = 5
                        emote = random.choice(["Kreygasm", "KevinTurtle", "TriHard"])
                        emotewall = " ".join([emote]*3)
                        self.bot.channelMsg("/me %s | %s guessed %s correctly first! They win %d %s. | %s" % (emotewall, user, self.word, prize, config.currencyPlural, emotewall))
                        userData = self.bot.getUserDetails(user)
                        
                        theirNewBal = userData["balance"] + prize
                        queryArgList = (theirNewBal, user, userData["balance"])
                        self.bot.execQueryModify("UPDATE users SET balance = ?, contests_won = contests_won + 1 WHERE twitchname = ? AND balance = ?", queryArgList)
                        self.bot.updateHighestBalance(userData, theirNewBal)
                        logArgList = (user, "hangman", self.word, prize, int(time.time()), self.bot.factory.channel)
                        self.bot.execQueryModify("INSERT INTO contestwins (twitchname, gameid, answer, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgList)
                        self.contestmanager.contestIsDone()
                        return
                    else:
                        # did it match the current clues?
                        currentCluesMatched = True
                        for i in xrange(0, len(self.word)):
                            if self.word[i] in self.guessedLetters and self.word[i] != lowerword[i]:
                                currentCluesMatched = False
                                break
                        
                        if currentCluesMatched:
                            # they're out
                            self.bot.channelMsg("Sorry %s, that guess is incorrect, you're out for this round." % user)
                            self.fullGuesses.append(user)
                            return
                    
    
    def end(self):
        emote = random.choice(["BibleThump"], ":(")
        emotewall = " ".join([emote]*3)
        self.bot.channelMsg("/me %s | No-one guessed correctly, the correct answer was %s. Too bad! | %s" % (emotewall, self.word, emotewall))
