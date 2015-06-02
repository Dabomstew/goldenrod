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
        bot.channelMsg("%s -> For the full luckypeople leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=luckypeople" % user)
        return
    
    if topwhat == 1:
        topHandout = bot.execQuerySelectOne("SELECT * FROM handouts ORDER BY amount DESC LIMIT 1")
        finalMessage = "%s -> The luckiest handout was for %d %s, received by %s." % (user, topHandout["amount"], config.currencyName if (topHandout["amount"] == 1) else config.currencyPlural, topHandout["twitchname"])
        bot.channelMsg(finalMessage.encode("utf-8"))
    else:
        topHandouts = bot.execQuerySelectMultiple("SELECT * FROM handouts ORDER BY amount DESC LIMIT %d" % topwhat)
        finalMessage = "%s -> The luckiest %d handouts are: " % (user, topwhat)
        finalMessage += ", ".join("%s (%d %s)" % (handout["twitchname"], handout["amount"], config.currencyName if (handout["amount"] == 1) else config.currencyPlural) for handout in topHandouts)
        bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"