# coding=utf-8
import random
import time
import goldenrod, config

def execute(parser, bot, user, args):
    bot.sendInfoMessage("leaderboards", user, "For more detailed leaderboards go here - http://twitchbot.dabomstew.com/goldenrod/leaderboards.php")
        
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

