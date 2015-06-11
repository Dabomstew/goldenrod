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
        bot.addressUser(user, "For the full bigslots leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=bigslots")
        return
    
    if topwhat == 1:
        topWin = bot.execQuerySelectOne("SELECT * FROM slots WHERE balChange > 0 AND twitchname != ? ORDER BY balChange DESC LIMIT %d" % topwhat, (config.botOwner,))
        finalMessage = "The biggest slots win is held by %s with a %s win of %d %s." % (topWin["twitchname"], topWin["reelOne"], topWin["balChange"], config.currencyPlural)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    else:      
        topPlayers = bot.execQuerySelectMultiple("SELECT * FROM slots WHERE balChange > 0 AND twitchname != ? ORDER BY balChange DESC LIMIT %d" % topwhat, (config.botOwner,))
        finalMessage = "The biggest %d slots wins are: " % topwhat
        finalMessage += ", ".join("%s (%s, %d %s)" % (player["twitchname"], player["reelOne"], player["balChange"], config.currencyName if (player["balChange"] == 1) else config.currencyPlural) for player in topPlayers)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

