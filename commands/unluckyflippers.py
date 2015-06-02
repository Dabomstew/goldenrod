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
        bot.channelMsg("%s -> For the full unluckyflippers leaderboard go here: http://twitchbot.dabomstew.com/goldenrod/leaderboards.php?board=unluckyflippers" % user)
        return
        
    # make sure there is a user to pick, the cheap way
    userData = bot.getUserDetails(user)
    
    # parse their choice
    if topwhat == 1:
        topPlayer = bot.execQuerySelectOne("SELECT * FROM users WHERE (coins_won+coins_lost) > 0 AND twitchname != ? ORDER BY (coins_lost - coins_won) DESC, (coins_won + coins_lost) ASC LIMIT 1", (config.botOwner,))
        finalMessage = "%s -> The unluckiest coinflipper is %s with %d coin wins and %d coin losses." % (user, topPlayer["twitchname"], topPlayer["coins_won"], topPlayer["coins_lost"])
        bot.channelMsg(finalMessage.encode("utf-8"))
    else:
        topPlayers = bot.execQuerySelectMultiple("SELECT * FROM users WHERE (coins_won+coins_lost) > 0 AND twitchname != ? ORDER BY (coins_lost - coins_won) DESC, (coins_won + coins_lost) ASC LIMIT %d" % topwhat, (config.botOwner,))
        finalMessage = "%s -> The unluckiest %d coinflippers are: " % (user, topwhat)
        finalMessage += ", ".join("%s (%d-%d)" % (player["twitchname"], player["coins_won"], player["coins_lost"]) for player in topPlayers)
        bot.channelMsg(finalMessage.encode("utf-8"))
    
def requiredPerm():
    return "anyone"