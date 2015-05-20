import config
import random
import datetime, time

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
            isWinner = False
            newWins = userData["coins_won"]
            newLosses = userData["coins_lost"]
            if coinFlip == 1:
                newBal = userData["balance"]+gamble
                isWinner = True
                bot.channelMsg("%s -> Heads. +%d %s." % (user, gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newWins = newWins + 1
            else:
                newBal = userData["balance"]-gamble
                bot.channelMsg("%s -> Tails. -%d %s." % (user, gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newLosses = newLosses + 1
            
            timeNow = int(time.time())
            queryArgs = (newBal, timeNow, datetime.datetime.now(), newWins, newLosses, user, userData["balance"])
            bot.execQueryModify("UPDATE users SET balance = ?, last_game = ?, last_activity = ?, coins_won = ?, coins_lost = ? WHERE twitchname = ? AND balance = ?", queryArgs)
            bot.updateHighestBalance(userData, newBal)
            logArgs = (user, gamble, True if gamble == userData["balance"] else False, isWinner, datetime.datetime.now())
            bot.execQueryModify("INSERT INTO coinflips (twitchname, amount, yoloflip, winner, whenHappened) VALUES(?, ?, ?, ?, ?)", logArgs)
        else:
            bot.channelMsg("%s -> Not able to gamble that amount." % user)
    else:
        if config.showCooldowns:
            bot.channelMsg("%s -> On cooldown. (%d secs)" % (user, canPlay))
    
def requiredPerm():
    return "anyone"