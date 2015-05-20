import config
import random
import datetime, time

def execute(parser, bot, user, args):
    topwhat = 5
        
    topPlayers = bot.execQuerySelectMultiple("SELECT * FROM handouts ORDER BY amount DESC LIMIT %d" % topwhat)
    finalMessage = "%s -> The luckiest %d handouts are: " % (user, topwhat)
    for player in topPlayers:
        finalMessage = "%s%s (%d %s), " % (finalMessage, player["twitchname"], player["amount"], config.currencyName if (player["amount"] == 1) else config.currencyPlural)
    
    finalMessage = finalMessage[:-2]
    bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"