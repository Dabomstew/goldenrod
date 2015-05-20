import config
import random
import datetime, time, math

def execute(parser, bot, user, args):
    if "bot" in user:
        bot.channelMsg("%s -> LOL nope." % user)
        return
        
    altCheck = bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (user,))
    
    if altCheck != None:
        bot.channelMsg("%s -> Known alts aren't allowed to donate." % user)
        return
        
    userData = bot.getUserDetails(user)
    arglist = args.split()
    try:
        amount = int(arglist[1])
    except ValueError:
        bot.channelMsg("%s -> Invalid amount to donate." % user)
        return
     
    if amount <= 0 or amount > userData["balance"]:
        bot.channelMsg("%s -> Invalid amount to donate." % user)
        return
        
    tax = 0
    
    if amount > 50:
        taxable = min(amount - 50, 50)
        tax = tax + int(math.floor(taxable*3/10))
        
    if amount > 100:
        taxable = min(amount - 100, 900)
        tax = tax + int(math.floor(taxable*4/10))
        
    if amount > 1000:
        taxable = min(amount - 1000, 9000)
        tax = tax + int(math.floor(taxable*6/10))
        
    if amount > 10000:
        taxable = amount - 10000
        tax = tax + int(math.floor(taxable*9/10))
    
    taxedAmount = amount - tax
    
    otherUserTry = arglist[0].lower()
    
    if otherUserTry == user:
        bot.channelMsg("%s -> You can't donate to yourself." % user)
        return
        
    if otherUserTry in user or user in otherUserTry:
        bot.channelMsg("%s -> Try harder please." % user)
        return
    
    otherUser = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (otherUserTry,))
    if otherUser == None:
        bot.channelMsg("%s -> %s hasn't played on Goldenrod yet." % (user, otherUserTry))
    else:
        theirNewBal = otherUser["balance"] + taxedAmount
        ourNewBal = userData["balance"] - amount
        firstArgList = (ourNewBal, datetime.datetime.now(), user, userData["balance"])
        if bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", firstArgList) == 1:
            secondArgList = (theirNewBal, otherUserTry, otherUser["balance"])
            bot.execQueryModify("UPDATE users SET balance = ? WHERE twitchname = ? AND balance = ?", secondArgList)
            bot.updateHighestBalance(otherUser, theirNewBal)
            outputList = (user, amount, config.currencyName if (amount == 1) else config.currencyPlural, otherUserTry, taxedAmount, config.currencyName if (taxedAmount == 1) else config.currencyPlural)
            bot.channelMsg("%s -> Donated %d %s to %s, they received %d %s." % outputList)
            logArgs = (user, otherUserTry, amount, datetime.datetime.now())
            bot.execQueryModify("INSERT INTO donations (fromPlayer, toPlayer, amount, whenHappened) VALUES(?, ?, ?, ?)", logArgs)
        else:
            bot.channelMsg("%s -> Donation failed." % user)
    
def requiredPerm():
    return "anyone"