import config
import random
import datetime, time
from twisted.internet import reactor

def execute(parser, bot, user, args):
    userData = bot.getUserDetails(user)
    canPlay = bot.canPlayGame(userData)
    if canPlay == 0:
        gamble = 0
        try:
            gamble = int(args)
        except ValueError:
            bot.channelMsg("%s -> Invalid argument." % user)
            return
        
        if gamble > 0 and gamble <= userData["balance"]:
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
                bot.channelMsg("%s -> Heads. +%d %s." % (user, gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newWins += 1
            else:
                newBal -= gamble
                newProfit -= gamble
                bot.channelMsg("%s -> Tails. -%d %s." % (user, gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newLosses += 1
            
            timeNow = int(time.time())
            queryArgs = (newBal, newProfit, timeNow, timeNow, newWins, newLosses, user, userData["balance"])
            bot.execQueryModify("UPDATE users SET balance = ?, coin_profit = ?, last_game = ?, last_activity = ?, coins_won = ?, coins_lost = ? WHERE twitchname = ? AND balance = ?", queryArgs)
            bot.updateHighestBalance(userData, newBal)
            logArgs = (user, gamble, True if gamble == userData["balance"] else False, isWinner, timeNow, bot.factory.channel)
            bot.execQueryModify("INSERT INTO coinflips (twitchname, amount, yoloflip, winner, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", logArgs)
        else:
            bot.channelMsg("%s -> Not able to gamble that amount." % user)
    else:
        reactor.whisperer.sendWhisper(user, "On cooldown. (%d secs)" % canPlay)
    
def requiredPerm():
    return "anyone"