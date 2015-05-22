import config
import datetime, time

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    bot.contestsEnabled = True
    bot.contestManager.startNextContest = int(time.time())-1
    bot.channelMsg("%s -> One contest, coming right up." % (user))
    
def requiredPerm():
    return "owner"
    