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
    
    bot.execQueryModify("INSERT INTO alts (twitchname, whenHappened) VALUES(?, ?)", (otherUserTry,int(time.time())))
    bot.channelMsg("%s -> Flagged %s as an alt, they are no longer allowed to donate." % (user, otherUserTry))
    
def requiredPerm():
    return "owner"