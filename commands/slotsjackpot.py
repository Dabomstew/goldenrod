import config
import random
import datetime, time
import math

def execute(parser, bot, user, args):
    slotsPool = bot.execQuerySelectOne("SELECT * FROM slotspool")
    bot.channelMsg("%s -> The current slots jackpot is %d %s." % (user, slotsPool["slotspool"], config.currencyPlural))
    
def requiredPerm():
    return "anyone"