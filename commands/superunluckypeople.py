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
        bot.addressUser(user, "For the full superunluckypeople leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=superunluckypeople")
        return
        
    if topwhat == 1:
        topPlayer = bot.execQuerySelectOne("SELECT twitchname, COUNT(*) AS zeroCount FROM handouts WHERE amount = 0 GROUP BY twitchname ORDER BY COUNT(*) DESC LIMIT 1")
        finalMessage = "The person with the most gen1 miss handouts is %s with %d." % (topPlayer["twitchname"], topPlayer["zeroCount"])
        bot.addressUser(user, finalMessage.encode("utf-8"))
    else:    
        topPlayers = bot.execQuerySelectMultiple("SELECT twitchname, COUNT(*) AS zeroCount FROM handouts WHERE amount = 0 GROUP BY twitchname ORDER BY COUNT(*) DESC LIMIT %d" % topwhat)
        finalMessage = "The %d people with the most gen1 miss handouts are: " % topwhat
        finalMessage += ", ".join("%s (%d)" % (player["twitchname"], player["zeroCount"]) for player in topPlayers)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

