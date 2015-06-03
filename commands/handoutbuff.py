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
    
    bot.channelMsg("Fed up by 1-point handouts? Find the magic word to include in your !handout message to get a buff to the possible handouts. The word will change periodically. Current clue: Pretty much universally loved by Twitch users.")
        
def requiredPerm():
    return "anyone"