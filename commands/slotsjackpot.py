import config
import random
import datetime, time
import math

def execute(parser, bot, user, args):
    slotsPool = bot.execQuerySelectOne("SELECT * FROM slotspool")
    bot.addressUser(user, "The current slots jackpot is %d %s." % (slotsPool["slotspool"], config.currencyPlural))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

