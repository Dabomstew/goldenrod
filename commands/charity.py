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
        bot.channelMsg("%s -> Invalid amount to give." % user)
        return
     
    if amount <= 0:
        bot.channelMsg("%s -> Invalid amount to give." % user)
        return
    
    otherUserTry = arglist[0].lower()
    
    otherUser = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (otherUserTry,))
    if otherUser == None:
        bot.channelMsg("%s -> %s hasn't played on Goldenrod yet." % (user, otherUserTry))
    else:
        theirNewBal = otherUser["balance"] + amount
        secondArgList = (theirNewBal, otherUserTry, otherUser["balance"])
        bot.execQueryModify("UPDATE users SET balance = ? WHERE twitchname = ? AND balance = ?", secondArgList)
        bot.updateHighestBalance(otherUser, theirNewBal)
        bot.channelMsg("%s -> Gave %d %s to %s." % (user, amount, config.currencyName if (amount == 1) else config.currencyPlural, otherUserTry))
        logArgs = (otherUserTry, amount, int(time.time()), bot.factory.channel)
        bot.execQueryModify("INSERT INTO charity (twitchname, amount, whenHappened, channel) VALUES(?, ?, ?, ?)", logArgs)
    
def requiredPerm():
    return "owner"