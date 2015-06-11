import config
import random
import datetime, time

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    userData = bot.getUserDetails(user)
    arglist = args.split()
    try:
        amount = int(arglist[1])
    except ValueError:
        bot.addressUser(user, "Invalid amount to tax.")
        return
     
    if amount <= 0:
        bot.addressUser(user, "Invalid amount to tax.")
        return
    
    otherUserTry = arglist[0].lower()
    
    otherUser = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (otherUserTry,))
    if otherUser == None:
        bot.addressUser(user, "%s hasn't played on Goldenrod yet." % otherUserTry)
    else:
        theirNewBal = otherUser["balance"] - amount
        secondArgList = (theirNewBal, otherUserTry, otherUser["balance"])
        bot.execQueryModify("UPDATE users SET balance = ? WHERE twitchname = ? AND balance = ?", secondArgList)
        bot.addressUser(user, "Taxed %d %s from %s." % (amount, config.currencyName if (amount == 1) else config.currencyPlural, otherUserTry))
        logArgs = (otherUserTry, amount, int(time.time()), bot.factory.channel)
        bot.execQueryModify("INSERT INTO taxes (twitchname, amount, whenHappened, channel) VALUES(?, ?, ?, ?)", logArgs)
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True

