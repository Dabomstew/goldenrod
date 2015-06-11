import config
import random
import datetime, time

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    
    print repr(random.getstate())
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True

