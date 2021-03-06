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
        bot.addressUser(user, "For the full alltimetop leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=alltimetop")
        return
        
    # make sure there is a user to pick, the cheap way
    userData = bot.getUserDetails(user)
    
    # parse their choice
    if topwhat == 1:
        topPlayer = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname != ? ORDER BY highest_balance DESC LIMIT 1", (config.botOwner, ))
        finalMessage = "The highest balance ever was held by %s with %d %s." % (topPlayer["twitchname"], topPlayer["highest_balance"], config.currencyName if (topPlayer["highest_balance"] == 1) else config.currencyPlural)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    else:
        topPlayers = bot.execQuerySelectMultiple("SELECT * FROM users WHERE twitchname != ? ORDER BY highest_balance DESC LIMIT %d" % topwhat, (config.botOwner, ))
        finalMessage = "The top %d players of all time were: " % topwhat
        finalMessage += ", ".join("%s (%d %s)" % (player["twitchname"], player["highest_balance"], config.currencyName if (player["highest_balance"] == 1) else config.currencyPlural) for player in topPlayers)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

