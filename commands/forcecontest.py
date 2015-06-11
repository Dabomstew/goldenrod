import config
import datetime, time

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    bot.contestsEnabled = True
    bot.contestManager.startNextContest = int(time.time())-1
    bot.addressUser(user, "One contest, coming right up.")
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return False


    