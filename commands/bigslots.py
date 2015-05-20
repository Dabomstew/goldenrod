import config
import random
import datetime, time

def execute(parser, bot, user, args):
    topwhat = 5
        
    topPlayers = bot.execQuerySelectMultiple("SELECT * FROM slots WHERE balChange > 0 ORDER BY balChange DESC LIMIT %d" % topwhat)
    finalMessage = "%s -> The biggest %d slots wins are: " % (user, topwhat)
    for player in topPlayers:
        finalMessage = "%s%s (%s, %d %s), " % (finalMessage, player["twitchname"], player["reelOne"], player["balChange"], config.currencyName if (player["balChange"] == 1) else config.currencyPlural)
    
    finalMessage = finalMessage[:-2]
    bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"