import config
import random
import datetime, time

def execute(parser, bot, user, args):
    topwhat = 5
    try:
        topwhat = int(args)
    except ValueError:
        topwhat = 5
    
    if topwhat < 1:
        topwhat = 1
    
    if topwhat > 10:
        topwhat = 10
    
    if topwhat == 1:
        topWin = bot.execQuerySelectOne("SELECT * FROM slots WHERE balChange > 0 AND twitchname != ? ORDER BY balChange DESC LIMIT %d" % topwhat, (config.botOwner,))
        finalMessage = "%s -> The biggest slots win is held by %s with a %s win of %d %s." % (user, topWin["twitchname"], topWin["reelOne"], topWin["balChange"], config.currencyPlural)
        bot.channelMsg(finalMessage.encode("utf-8"))
    else:      
        topPlayers = bot.execQuerySelectMultiple("SELECT * FROM slots WHERE balChange > 0 AND twitchname != ? ORDER BY balChange DESC LIMIT %d" % topwhat, (config.botOwner,))
        finalMessage = "%s -> The biggest %d slots wins are: " % (user, topwhat)
        finalMessage += ", ".join("%s (%s, %d %s)" % (player["twitchname"], player["reelOne"], player["balChange"], config.currencyName if (player["balChange"] == 1) else config.currencyPlural) for player in topPlayers)
        bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"