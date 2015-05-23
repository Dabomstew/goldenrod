import config
import random
import datetime, time, math

def taxOn(amount):
    tax = 0
    if amount > 200:
        taxable = min(amount - 200, 300)
        tax = tax + int(math.floor(taxable*3/10))
        
    if amount > 500:
        taxable = min(amount - 500, 500)
        tax = tax + int(math.floor(taxable*4/10))
        
    if amount > 1000:
        taxable = min(amount - 1000, 9000)
        tax = tax + int(math.floor(taxable*6/10))
        
    if amount > 10000:
        taxable = amount - 10000
        tax = tax + int(math.floor(taxable*9/10))
        
    return tax

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
    timeNow = int(time.time())
    try:
        amount = int(arglist[1])
    except ValueError:
        bot.channelMsg("%s -> Invalid amount to donate." % user)
        return
     
    if amount <= 0 or amount > userData["balance"]:
        bot.channelMsg("%s -> Invalid amount to donate." % user)
        return
        
    otherUserTry = arglist[0].lower()
    
    if otherUserTry == user:
        bot.channelMsg("%s -> You can't donate to yourself." % user)
        return
        
    if otherUserTry in user or user in otherUserTry:
        bot.channelMsg("%s -> Try harder please." % user)
        return
        
    historyRow = bot.execQuerySelectOne("SELECT COALESCE(SUM(amount),0) AS totalDonated FROM donations WHERE fromPlayer = ? AND toPlayer = ? AND whenHappened >= ?", (user, otherUserTry, timeNow - 86400*2))
    oldAmount = historyRow["totalDonated"]
    newAmount = oldAmount + amount
    oldTax = taxOn(oldAmount)
    newTax = taxOn(newAmount)
    tax = newTax - oldTax
    
    taxedAmount = amount - tax
    
    otherUser = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (otherUserTry,))
    if otherUser == None:
        bot.channelMsg("%s -> %s hasn't played on Goldenrod yet." % (user, otherUserTry))
    else:
        theirNewBal = otherUser["balance"] + taxedAmount
        ourNewBal = userData["balance"] - amount
        firstArgList = (ourNewBal, int(time.time()), user, userData["balance"])
        if bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", firstArgList) == 1:
            secondArgList = (theirNewBal, otherUserTry, otherUser["balance"])
            bot.execQueryModify("UPDATE users SET balance = ? WHERE twitchname = ? AND balance = ?", secondArgList)
            bot.updateHighestBalance(otherUser, theirNewBal)
            outputList = (user, amount, config.currencyName if (amount == 1) else config.currencyPlural, otherUserTry, taxedAmount, config.currencyName if (taxedAmount == 1) else config.currencyPlural)
            bot.channelMsg("%s -> Donated %d %s to %s, they received %d %s." % outputList)
            logArgs = (user, otherUserTry, amount, int(time.time()), bot.factory.channel)
            bot.execQueryModify("INSERT INTO donations (fromPlayer, toPlayer, amount, whenHappened, channel) VALUES(?, ?, ?, ?, ?)", logArgs)
        else:
            bot.channelMsg("%s -> Donation failed." % user)
    
def requiredPerm():
    return "anyone"