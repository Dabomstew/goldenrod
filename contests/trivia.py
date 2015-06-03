# coding=utf-8
# shell class

import random
import config
import datetime, time
import math

class Game:

    def __init__(self, contestmanager):
        self.contestmanager = contestmanager
        self.bot = contestmanager.bot
        self.questionData = None
        self.answers = []
        self.startTime = 0
        
    def start(self):
        self.startTime = int(time.time())
        # first select a grouping
        groupData = self.bot.execQuerySelectOne("SELECT question_grouping AS chosenGroup FROM trivia_questions WHERE used_in_cycle = 0 GROUP BY question_grouping ORDER BY RANDOM() LIMIT 1")
        if groupData == None:
            # no questions left
            self.bot.execQueryModify("UPDATE trivia_questions SET used_in_cycle = 0")
            groupData = self.bot.execQuerySelectOne("SELECT question_grouping AS chosenGroup FROM trivia_questions WHERE used_in_cycle = 0 GROUP BY question_grouping ORDER BY RANDOM() LIMIT 1")
        self.questionData = self.bot.execQuerySelectOne("SELECT * FROM trivia_questions WHERE question_grouping = ? AND used_in_cycle = 0 ORDER BY RANDOM() LIMIT 1", (groupData["chosenGroup"], ))
        self.bot.execQueryModify("UPDATE trivia_questions SET used_in_cycle = 1 WHERE id = ?", (self.questionData["id"],))
        questionStr = "/me Kappa Kappa Kappa |  Trivia! %s | Kappa Kappa Kappa" % (self.questionData["question"].encode("utf-8"))
        self.bot.channelMsg(questionStr)
        answerRows = self.bot.execQuerySelectMultiple("SELECT * FROM trivia_answers WHERE question_id = ?", (self.questionData["id"],))
        for answerRow in answerRows:
            self.answers.append(answerRow["answer"].encode("utf-8"))
        
    def processMessage(self, user, message):
        if message.strip():
            if "bot" in user:
                # no bots
                return
            
            altCheck = self.bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (user,))
                
            if altCheck != None:
                # no alts either
                return
            
            msglower = message.strip().lower()
            msglower = msglower.replace("é", "e")
            
            if msglower.startswith("!guess "):
                msglower = msglower[7:]
            
            if msglower.startswith("pokemon "):
                msglower = msglower[8:]
                
            if msglower in self.answers:
                # woo
                prize = config.triviaPrizes[self.questionData["difficulty"]]
                diffName = config.triviaDifficulties[self.questionData["difficulty"]]
                elapsedTime = int(time.time()) - self.startTime
                if elapsedTime >= config.triviaPrizeReducFirst:
                    prize = int(prize/2)
                    
                if elapsedTime >= config.triviaPrizeReducSecond:
                    prize = int(prize/2)  

                wonCheck = self.bot.execQuerySelectOne("SELECT * FROM trivia_winners WHERE twitchname = ? AND question_id = ? LIMIT 1", (user, self.questionData["id"]))
                if wonCheck != None:
                    prize = int(prize/2)
                    
                emote = random.choice(["Kreygasm", "KevinTurtle", "TriHard"])
                emotewall = " ".join([emote]*3)
                
                msgArgs = (emotewall, user, msglower, diffName, elapsedTime, prize, config.currencyPlural, emotewall)
                self.bot.channelMsg("/me %s | %s's answer of %s was correct! For answering a %s question in %d seconds they gain %d %s. | %s" % msgArgs)
                userData = self.bot.getUserDetails(user)
                
                theirNewBal = userData["balance"] + prize
                queryArgList = (theirNewBal, user, userData["balance"])
                self.bot.execQueryModify("UPDATE users SET balance = ?, contests_won = contests_won + 1 WHERE twitchname = ? AND balance = ?", queryArgList)
                self.bot.updateHighestBalance(userData, theirNewBal)
                logArgList = (user, "trivia", msglower, prize, int(time.time()), self.bot.factory.channel)
                self.bot.execQueryModify("INSERT INTO contestwins (twitchname, gameid, answer, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgList)
                secondlogArgList = (user, self.questionData["id"], elapsedTime, prize, int(time.time()), self.bot.factory.channel)
                self.bot.execQueryModify("INSERT INTO trivia_winners (twitchname, question_id, timeTaken, reward, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", secondlogArgList)
                self.contestmanager.contestIsDone()
                return
                    
    
    def end(self):
        emote = random.choice(["BibleThump"], ":(")
        emotewall = " ".join([emote]*3)
        self.bot.channelMsg("/me %s | No-one answered correctly. Too bad! Try again next time. | %s" % (emotewall, emotewall))
