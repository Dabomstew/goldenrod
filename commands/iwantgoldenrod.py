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
    
    bot.channelMsg("No, no you don't. (If you're serious, message Dabomstew over Twitch PM or @Dabomstew on Twitter to discuss it.)")
        
def requiredPerm():
    return "anyone"