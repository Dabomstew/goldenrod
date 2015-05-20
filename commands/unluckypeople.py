import config
import random
import datetime, time

def execute(parser, bot, user, args):
    topwhat = 5
        
    topPlayers = bot.execQuerySelectMultiple("SELECT twitchname, COUNT(*) AS oneCount FROM handouts WHERE amount = 1 GROUP BY twitchname ORDER BY COUNT(*) DESC LIMIT %d" % topwhat)
    finalMessage = "%s -> The %d people with the most 1-point handouts are: " % (user, topwhat)
    for player in topPlayers:
        finalMessage = "%s%s (%d), " % (finalMessage, player["twitchname"], player["oneCount"])
    
    finalMessage = finalMessage[:-2]
    bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"