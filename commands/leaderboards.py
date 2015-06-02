# coding=utf-8
import random
import time
import goldenrod, config

cmdlisttime = 0

def execute(parser, bot, user, args):
    global cmdlisttime
    newluckypls = time.time()
    if cmdlisttime > newluckypls - 60 and not parser.checkPerms(bot, user, "mod"):
        return
    else:
        cmdlisttime = newluckypls
    
    bot.channelMsg("For more detailed leaderboards go here - http://twitchbot.dabomstew.com/goldenrod/leaderboards.php")
        
def requiredPerm():
    return "anyone"