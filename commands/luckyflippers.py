import config
import random
import datetime, time

def execute(parser, bot, user, args):
    topwhat = 3
    try:
        topwhat = int(args)
    except ValueError:
        topwhat = 3
    
    if topwhat < 1:
        topwhat = 1
    
    if topwhat > 10:
        topwhat = 10
        
    # make sure there is a user to pick, the cheap way
    userData = bot.getUserDetails(user)
    
    # parse their choice
    if topwhat == 1:
        topPlayer = bot.execQuerySelectOne("SELECT * FROM users WHERE (coins_won+coins_lost) > 0 ORDER BY (coins_won - coins_lost) DESC, (coins_won + coins_lost) ASC LIMIT 1")
        finalMessage = "%s -> The luckiest coinflipper is %s with %d coin wins and %d coin losses." % (user, topPlayer["twitchname"], topPlayer["coins_won"], topPlayer["coins_lost"])
        bot.channelMsg(finalMessage.encode("utf-8"))
    else:
        topPlayers = bot.execQuerySelectMultiple("SELECT * FROM users WHERE (coins_won+coins_lost) > 0 ORDER BY (coins_won - coins_lost) DESC, (coins_won + coins_lost) ASC LIMIT %d" % topwhat)
        finalMessage = "%s -> The luckiest %d coinflippers are: " % (user, topwhat)
        for player in topPlayers:
            finalMessage = "%s%s (%d-%d), " % (finalMessage, player["twitchname"], player["coins_won"], player["coins_lost"])
        
        finalMessage = finalMessage[:-2]
        bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"