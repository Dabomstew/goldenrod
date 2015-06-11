import config
import random
import datetime, time

def execute(parser, bot, user, args):

    econData = bot.execQuerySelectOne("SELECT SUM(balance) AS allPoints FROM users WHERE twitchname != ?", (config.botOwner,))
    countData = bot.execQuerySelectOne("SELECT COUNT(*) AS userCount FROM users WHERE twitchname != ?", (config.botOwner,))
    limitClause = countData["userCount"]/10
    econTopTen = bot.execQuerySelectMultiple("SELECT balance FROM users WHERE twitchname != ? ORDER BY balance DESC LIMIT %d" % limitClause, (config.botOwner,))
    topsBalance = 0
    for econEntry in econTopTen:
        topsBalance = topsBalance + econEntry["balance"]
    coinData = bot.execQuerySelectOne("SELECT SUM(amount) AS allLosses FROM coinflips WHERE winner = 0")
    bot.addressUser(user, "There are currently %d %s in circulation of which %d%% is held by the top 10%% of users. %d %s have been lost forever to !coin or !yolocoin." % (econData["allPoints"], config.currencyPlural, topsBalance*100/econData["allPoints"], coinData["allLosses"], config.currencyPlural))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

