import config
import random
import datetime, time
from twisted.internet import reactor

def execute(parser, bot, user, args):
    if bot.inQuietMode:
        bot.tellAboutQuietMode(user)
        return
        
    userData = bot.getUserDetails(user)
    canPlay = bot.canPlayGame(userData)
    if canPlay == 0:
        gamble = userData["balance"]
        if gamble > 0:
            coinFlip = random.randint(1, 2)
            newBal = userData["balance"]
            newProfit = userData["coin_profit"]
            isWinner = False
            newWins = userData["coins_won"]
            newLosses = userData["coins_lost"]
            if coinFlip == 1:
                newBal += gamble
                newProfit += gamble
                isWinner = True
                bot.addressUser(user, "Heads. +%d %s." % (gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newWins += 1
            else:
                newBal -= gamble
                newProfit -= gamble
                bot.addressUser(user, "Tails. -%d %s." % (gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newLosses += 1
                if gamble >= 100:
                    bot.channelMsg("/me RIP %s 2015-2015" % user)
            
            timeNow = int(time.time())
            queryArgs = (newBal, newProfit, timeNow, timeNow, newWins, newLosses, user, userData["balance"])
            bot.execQueryModify("UPDATE users SET balance = ?, coin_profit = ?, last_game = ?, last_activity = ?, coins_won = ?, coins_lost = ? WHERE twitchname = ? AND balance = ?", queryArgs)
            bot.updateHighestBalance(userData, newBal)
            logArgs = (user, gamble, True, isWinner, timeNow, bot.factory.channel)
            bot.execQueryModify("INSERT INTO coinflips (twitchname, amount, yoloflip, winner, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgs)
        else:
            bot.addressUser(user, "No %s to gamble." % config.currencyPlural)
    else:
        reactor.whisperer.sendWhisper(user, "On cooldown. (%d secs)" % canPlay)
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return False

