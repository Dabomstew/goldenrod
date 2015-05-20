import config
import random
import datetime, time

def execute(parser, bot, user, args):
    topwhat = 5
        
    topPlayers = bot.execQuerySelectMultiple("SELECT * FROM slots WHERE balChange > 0 AND twitchname != ? ORDER BY balChange DESC LIMIT %d" % topwhat, (config.botOwner,))
    finalMessage = "%s -> The biggest %d slots wins are: " % (user, topwhat)
    finalMessage += ", ".join("%s (%s, %d %s)" % (player["twitchname"], player["reelOne"], player["balChange"], config.currencyName if (player["balChange"] == 1) else config.currencyPlural) for player in topPlayers)
    bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"