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
        bot.addressUser(user, "For the full toptalents leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=toptalents")
        return
        
    # make sure there is a user to pick, the cheap way
    userData = bot.getUserDetails(user)
    
    # parse their choice
    if topwhat == 1:
        topPlayer = bot.execQuerySelectOne("SELECT * FROM users ORDER BY contests_won DESC LIMIT 1")
        finalMessage = "The top contest player is %s with %d wins." % (topPlayer["twitchname"], topPlayer["contests_won"])
        bot.addressUser(user, finalMessage.encode("utf-8"))
    else:
        topPlayers = bot.execQuerySelectMultiple("SELECT * FROM users ORDER BY contests_won DESC LIMIT %d" % topwhat)
        finalMessage = "The top %d contest players are: " % topwhat
        finalMessage += ", ".join("%s (%d wins)" % (player["twitchname"], player["contests_won"]) for player in topPlayers)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

