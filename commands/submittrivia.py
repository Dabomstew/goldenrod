# coding=utf-8
import random
import time
import goldenrod, config

def execute(parser, bot, user, args):
    bot.sendInfoMessage("submittrivia", user, "If you want to submit new trivia questions go here - http://goo.gl/forms/QZnP8ZDrLr")
        
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

