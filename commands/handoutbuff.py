# coding=utf-8
import random
import time
import goldenrod, config

def execute(parser, bot, user, args):
    bot.sendInfoMessage("handoutbuff", user, "Fed up by 1-point handouts? Find the magic word to include in your !handout message to get a buff to the possible handouts. There will be a new word each week and the word will last for 48 hours regardless of whether it is found in that time or not. Current clue: %s" % config.handoutBuffClue)
        
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

