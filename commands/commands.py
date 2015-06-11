# coding=utf-8
import random
import time
import goldenrod, config

def execute(parser, bot, user, args):
    bot.sendInfoMessage("commands", user, "Currently available commands: http://pastebin.com/5CG7TkyH")
        
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

