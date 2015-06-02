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
        bot.channelMsg("%s -> For the full topbeggars leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=topbeggars" % user)
        return
        
    # make sure there is a user to pick, the cheap way
    userData = bot.getUserDetails(user)
    
    # parse their choice
    if topwhat == 1:
        topPlayer = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname != ? ORDER BY handouts DESC LIMIT 1", (config.botOwner,))
        finalMessage = "%s -> The top beggar is %s with %d handouts." % (user, topPlayer["twitchname"], topPlayer["handouts"])
        bot.channelMsg(finalMessage.encode("utf-8"))
    else:
        topPlayers = bot.execQuerySelectMultiple("SELECT * FROM users WHERE twitchname != ? ORDER BY handouts DESC LIMIT %d" % topwhat, (config.botOwner,))
        finalMessage = "%s -> The top %d beggars are: " % (user, topwhat)
        finalMessage += ", ".join("%s (%d handouts)" % (player["twitchname"], player["handouts"]) for player in topPlayers)
        bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"
