import config
import random
import datetime, time
import math
from twisted.internet import reactor

slotsReelOne = ["7", "Pika", "Karp", "BAR", "Cherry", "7", "Karp", "Diglett", "BAR", "Cherry", "7", "Pika", "Diglett", "BAR", "Cherry", "7", "Pika", "Karp"]
slotsReelTwo = ["7", "Karp", "Cherry", "Diglett", "Pika", "BAR", "Cherry", "Karp", "Diglett", "Cherry", "BAR", "Karp", "Diglett", "Cherry", "Pika", "7", "Karp", "Cherry"]
slotsReelThree = ["7", "Diglett", "Karp", "Cherry", "Pika", "Diglett", "Karp", "Cherry", "Pika", "Diglett", "Karp", "Cherry", "Pika", "Diglett", "BAR", "7", "Diglett", "Karp"]
def execute(parser, bot, user, args):
    if bot.inQuietMode:
        bot.tellAboutQuietMode(user)
        return
        
    if "bot" in user:
        bot.addressUser(user, "LOL nope.")
        return
        
    altCheck = bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (user,))
    
    if altCheck != None:
        bot.addressUser(user, "Known alts aren't allowed to play slots.")
        return
        
    userData = bot.getUserDetails(user)
    canPlay = bot.canPlayGame(userData)
    slotsPool = bot.execQuerySelectOne("SELECT * FROM slotspool")
    if canPlay == 0:
        gamble = 5
            
        if gamble > 0 and gamble <= userData["balance"]:
            reelOne = random.choice(slotsReelOne)
            reelTwo = random.choice(slotsReelTwo)
            reelThree = random.choice(slotsReelThree)
            if reelOne == "7" and reelTwo == "7" and reelThree != "7":
                trollReroll = random.randint(1, 8)
                if trollReroll < 7:
                    reelThree = "Diglett"
                else:
                    reelThree = "BAR"
            
            # Kappa b
            if (reelOne != reelTwo or reelOne != reelThree):
                trollReroll = random.randint(1, 100)
                if trollReroll <= 2:
                    reelOne = "7"
                    reelTwo = "7"
                    reelThree = "Diglett"
            
            newBal = userData["balance"]
            timeNow = int(time.time())
            if reelOne == reelTwo and reelOne == reelThree:
                # A WINNER IS YOU!
                winnings = slotsPool["slotspool"]
                if(reelOne == "7"):
                    winnings = winnings * 2
                elif(reelOne == "BAR"):
                    winnings = int(math.floor(winnings*3/2))
                
                argsListOne = (100, timeNow, timeNow, slotsPool["slotspool"])
                if bot.execQueryModify("UPDATE slotspool SET slotspool = ?, last_change = ?, last_winner = ? WHERE slotspool = ?", argsListOne) == 1:
                    newBal = newBal + winnings
                    argsListTwo = (newBal, timeNow, timeNow, user, userData["balance"])
                    bot.execQueryModify("UPDATE users SET balance = ?, last_game = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", argsListTwo)
                    bot.updateHighestBalance(userData, newBal)
                    bot.addressUser(user, "%s | %s | %s - Winner! +%d %s." % (reelOne, reelTwo, reelThree, winnings, config.currencyPlural))
            else:
                winnings = -gamble
                argsListOne = (slotsPool["slotspool"]+gamble, timeNow, slotsPool["slotspool"])
                if bot.execQueryModify("UPDATE slotspool SET slotspool = ?, last_change = ? WHERE slotspool = ?", argsListOne) == 1:
                    newBal = newBal - gamble
                    argsListTwo = (newBal, timeNow, timeNow, user, userData["balance"])
                    bot.execQueryModify("UPDATE users SET balance = ?, last_game = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", argsListTwo)
                    bot.addressUser(user, "%s | %s | %s - Not this time! -%d %s." % (reelOne, reelTwo, reelThree, gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
            
            logArgs = (user, reelOne, reelTwo, reelThree, True if (reelOne==reelTwo and reelOne==reelThree) else False, winnings, timeNow, bot.factory.channel)
            bot.execQueryModify("INSERT INTO slots (twitchname, reelOne, reelTwo, reelThree, winner, balChange, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", logArgs)
        else:
            bot.addressUser(user, "The slots cost 5 %s to play, you don't have enough." % config.currencyPlural)
    else:
        reactor.whisperer.sendWhisper(user, "On cooldown. (%d secs)" % canPlay)
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return False

