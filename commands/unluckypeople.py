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
        bot.addressUser(user, "For the full unluckypeople leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=unluckypeople")
        return
    
    if topwhat == 1:
        topPlayer = bot.execQuerySelectOne("SELECT twitchname, COUNT(*) AS oneCount FROM handouts WHERE amount = 1 GROUP BY twitchname ORDER BY COUNT(*) DESC LIMIT 1")
        finalMessage = "The person with the most 1-point handouts is %s with %d." % (topPlayer["twitchname"], topPlayer["oneCount"])
        bot.addressUser(user, finalMessage.encode("utf-8"))
    else:      
        topPlayers = bot.execQuerySelectMultiple("SELECT twitchname, COUNT(*) AS oneCount FROM handouts WHERE amount = 1 GROUP BY twitchname ORDER BY COUNT(*) DESC LIMIT %d" % topwhat)
        finalMessage = "The %d people with the most 1-point handouts are: " % topwhat
        finalMessage += ", ".join("%s (%d)" % (player["twitchname"], player["oneCount"]) for player in topPlayers)
        bot.addressUser(user, finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

