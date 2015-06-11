# coding=utf-8
import random
import time
import goldenrod, config

def execute(parser, bot, user, args):
    bot.sendInfoMessage("wantgoldenrod", user, "No, no you don't. (If you're serious, message Dabomstew over Twitch PM or @Dabomstew on Twitter to discuss it.)")
        
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

