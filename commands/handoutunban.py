import config
import random
import datetime, time

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    if not args:
        return
    userData = bot.getUserDetails(user)
    arglist = args.split()
    
    otherUserTry = arglist[0].lower()
    
    bot.execQueryModify("UPDATE users SET handout_ban = 0 WHERE twitchname = ?", (otherUserTry,))
    bot.addressUser(user, "Unbanned %s from handouts." % otherUserTry)
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True

