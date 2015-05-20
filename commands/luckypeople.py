import config
import random
import datetime, time

def execute(parser, bot, user, args):
    topwhat = 5
        
    topHandouts = bot.execQuerySelectMultiple("SELECT * FROM handouts ORDER BY amount DESC LIMIT %d" % topwhat)
    finalMessage = "%s -> The luckiest %d handouts are: " % (user, topwhat)
    finalMessage += ", ".join("%s (%d %s)" % (handout["twitchname"], handout["amount"], config.currencyName if (handout["amount"] == 1) else config.currencyPlural) for handout in topHandouts)
    bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"