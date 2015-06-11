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
        bot.addressUser(user, "For the full luckypeople leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=luckypeople")
        return
    
    if topwhat == 1:
        topHandout = bot.execQuerySelectOne("SELECT * FROM handouts ORDER BY amount DESC LIMIT 1")
        finalMessage = "The luckiest handout was for %d %s, received by %s." % (topHandout["amount"], config.currencyName if (topHandout["amount"] == 1) else config.currencyPlural, topHandout["twitchname"])
        bot.addressUser(user, finalMessage.encode("utf-8"))
    else:
        topHandouts = bot.execQuerySelectMultiple("SELECT * FROM handouts ORDER BY amount DESC LIMIT %d" % topwhat)
        finalMessage = "The luckiest %d handouts were: " % topwhat
        finalMessage += ", ".join("%s (%d %s)" % (handout["twitchname"], handout["amount"], config.currencyName if (handout["amount"] == 1) else config.currencyPlural) for handout in topHandouts)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

