import config
import random
import datetime, time

def execute(parser, bot, user, args):
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
                bot.channelMsg("%s -> Heads. +%d %s." % (user, gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newWins += 1
            else:
                newBal -= gamble
                newProfit -= gamble
                bot.channelMsg("%s -> Tails. -%d %s." % (user, gamble, config.currencyName if (gamble == 1) else config.currencyPlural))
                newLosses += 1
                if gamble >= 100:
                    bot.channelMsg("/me RIP %s 2015-2015" % user)
            
            timeNow = int(time.time())
            queryArgs = (newBal, newProfit, timeNow, datetime.datetime.now(), newWins, newLosses, user, userData["balance"])
            bot.execQueryModify("UPDATE users SET balance = ?, coin_profit = ?, last_game = ?, last_activity = ?, coins_won = ?, coins_lost = ? WHERE twitchname = ? AND balance = ?", queryArgs)
            bot.updateHighestBalance(userData, newBal)
            logArgs = (user, gamble, True, isWinner, datetime.datetime.now())
            bot.execQueryModify("INSERT INTO coinflips (twitchname, amount, yoloflip, winner, whenHappened) VALUES(?, ?, ?, ?, ?)", logArgs)
        else:
            bot.channelMsg("%s -> No %s to gamble." % (user, config.currencyPlural))
    else:
        if config.showCooldowns:
            bot.channelMsg("%s -> On cooldown. (%d secs)" % (user, canPlay))
    
def requiredPerm():
    return "anyone"