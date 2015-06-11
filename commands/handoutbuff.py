# coding=utf-8
import random
import time
import goldenrod, config

def execute(parser, bot, user, args):
    bot.sendInfoMessage("handoutbuff", user, "Fed up by 1-point handouts? Find the magic word to include in your !handout message to get a buff to the possible handouts. The word will change periodically. Current clue: %s" % config.handoutBuffClue)
        
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

