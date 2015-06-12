import config
import random
import datetime, time
import math
from twisted.internet import reactor

def execute(parser, bot, user, args):
    if bot.inQuietMode:
        bot.tellAboutQuietMode(user)
        return
        
    if "bot" in user:
        bot.addressUser(user, "LOL nope.")
        return
        
    altCheck = bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (user,))
    
    if altCheck != None:
        bot.addressUser(user, "Known alts aren't allowed to participate in duels.")
        return
        
    userData = bot.getUserDetails(user)
    timeNow = int(time.time())
    
    if args == None or args.strip() == "":
        bot.addressUser(user, "See %scommands to get the list of things you can do with %sduel." % (config.cmdChar, config.cmdChar))
        return
        
    bot.execQueryModify("DELETE FROM duel_requests WHERE expiry <= ?", (timeNow,))
    arglist = args.lower().split()
    if arglist[0] != "list" and arglist[0] != "challenge" and arglist[0] != "accept" and arglist[0] != "reject":
        arglist = ["challenge"] + arglist
        
    if arglist[0] == "list":
        # check duels
        myDuels = bot.execQuerySelectMultiple("SELECT * FROM duel_requests WHERE to_user = ? ORDER BY whenHappened ASC", (user,))
        if len(myDuels) == 0:
            bot.addressUser(user, "You have no pending duel challenges.")
        else:
            finalMessage = "You have %d pending duel challenges: " % (len(myDuels))
            for duel in myDuels:
                finalMessage = "%s%s - %d %s, " % (finalMessage, duel["from_user"], duel["amount"], config.currencyName if (duel["amount"] == 1) else config.currencyPlural)
            
            finalMessage = finalMessage[:-2]
            bot.addressUser(user, finalMessage.encode("utf-8"))
            
    elif arglist[0] == "challenge":
        # challenges are on cooldown
        canPlay = bot.canPlayGame(userData)
        if canPlay == 0:
            # do shit
            if len(arglist) < 3:
                bot.addressUser(user, "Invalid challenge (use %sduel challenge user amount)" % config.cmdChar)
                return
            try:
                amount = int(arglist[2])
            except ValueError:
                bot.addressUser(user, "Invalid amount to challenge for.")
                return
            if amount <= 0 or amount > userData["balance"]:
                bot.addressUser(user, "Invalid amount to challenge for.")
                return
            otherUserTry = arglist[1]
            if "bot" in otherUserTry:
                bot.addressUser(user, "You can't challenge bots.")
                return
            if otherUserTry == user:
                bot.addressUser(user, "You can't challenge yourself.")
                return
            if otherUserTry in user or user in otherUserTry:
                bot.addressUser(user, "Try harder please.")
                return
            otherAltCheck = bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (otherUserTry,))
    
            if otherAltCheck != None:
                bot.addressUser(user, "You can't challenge a known alt to a duel.")
                return
                
            otherUser = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (otherUserTry,))
            if otherUser == None:
                bot.addressUser(user, "%s hasn't played on Goldenrod yet." % otherUserTry)
                return
            else:
                if otherUser["balance"] < amount:
                    bot.addressUser(user, "%s doesn't have enough %s to accept your challenge." % (otherUserTry, config.currencyPlural))
                    return
                    
                otherDuelCheck = bot.execQuerySelectOne("SELECT * FROM duel_requests WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?) LIMIT 1", (user, otherUserTry, otherUserTry, user))
                if otherDuelCheck != None:
                    bot.addressUser(user, "There is already a pending duel between you and %s." % otherUserTry)
                    return
                
                # perfect, issue the challenge
                challengeArgs = (user, otherUserTry, amount, timeNow+config.duelRequestExpiry, timeNow, bot.factory.channel)
                bot.execQueryModify("INSERT INTO duel_requests (from_user, to_user, amount, expiry, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?)", challengeArgs)
                # update current user cooldown
                cdArgs = (timeNow, timeNow, user)
                bot.execQueryModify("UPDATE users SET last_game = ?, last_activity = ? WHERE twitchname = ?", cdArgs)
                # acknowledge the request in chat
                bot.addressUser(user, "You have issued the %d %s duel request to %s." % (amount, config.currencyName, otherUserTry))
                challengerMsgArgs = (user, amount, config.currencyName if (amount == 1) else config.currencyPlural, config.cmdChar, user, config.cmdChar, user)
                bot.addressUser(otherUserTry, "%s has challenged you to a duel for %d %s! Use %sduel accept %s to accept the request or %sduel reject %s to reject it." % challengerMsgArgs)
        else:
            reactor.whisperer.sendWhisper(user, "On cooldown. (%d secs)" % canPlay)
            
    elif arglist[0] == "accept":
        if len(arglist) < 2:
            bot.addressUser(user, "You didn't specify a user to accept the challenge from.")
            return
        
        otherUserTry = arglist[1]
        # check duels
        duelData = bot.execQuerySelectOne("SELECT * FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
        
        if duelData == None:
            bot.addressUser(user, "You don't have a pending challenge from %s. Use %sduel list to check your pending challenges." % (otherUserTry, config.cmdChar))
            return
        
        if duelData["amount"] > userData["balance"]:
            bot.addressUser(user, "You no longer have enough %s to accept this duel. Rejecting it instead..." % config.currencyPlural)
            bot.channelMsg("%s -> You no longer have enough %s to accept this duel. Rejecting it instead..." % (user, config.currencyPlural))
            bot.addressUser(otherUserTry, "%s was forced to reject your duel request due to not having enough %s left." % (user, config.currencyPlural))
            bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
            return
        
        otherUserData = bot.getUserDetails(otherUserTry)
        
        if duelData["amount"] > otherUserData["balance"]:
            bot.addressUser(user, "%s no longer has enough %s to participate in this duel. Rejecting it automatically..." % (otherUserTry, config.currencyPlural))
            bot.addressUser(otherUserTry, "%s was forced to reject your duel request because you no longer have enough %s left." % (user, config.currencyPlural))
            bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
            return
        
        bot.channelMsg("%s -> %s has accepted your challenge to duel for %d %s. Rolling dice..." % (otherUserTry, user, duelData["amount"], config.currencyName if (duelData["amount"] == 1) else config.currencyPlural))
        attackerRoll = random.randint(1, 6)
        defenderRoll = random.randint(1, 6)
        
        if attackerRoll > defenderRoll:
            winnerMsgArgs = (otherUserTry, attackerRoll, user, defenderRoll, otherUserTry, duelData["amount"]*2, config.currencyPlural)
            bot.channelMsg("KevinTurtle KevinTurtle KevinTurtle | %s rolled a %d and %s rolled a %d. %s wins the %d %s! | KevinTurtle KevinTurtle KevinTurtle" % winnerMsgArgs)
            loserBalArgs = (userData["balance"] - duelData["amount"], timeNow, userData["duel_profit"] - duelData["amount"], user, userData["balance"])
            if bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ?, duels_lost = duels_lost + 1, duel_profit = ? WHERE twitchname = ? AND balance = ?", loserBalArgs) == 1:
                winnerBalArgs = (otherUserData["balance"] + duelData["amount"], timeNow, otherUserData["duel_profit"] + duelData["amount"], otherUserTry, otherUserData["balance"])
                bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ?, duels_won = duels_won + 1, duel_profit = ? WHERE twitchname = ? AND balance = ?", winnerBalArgs)
                bot.updateHighestBalance(otherUserData, otherUserData["balance"]+duelData["amount"])
                resultLogArgs = (otherUserTry, user, attackerRoll, defenderRoll, duelData["amount"], otherUserTry, timeNow, bot.factory.channel)
                bot.execQueryModify("INSERT INTO duel_results (from_user, to_user, roll1, roll2, amount, winner, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", resultLogArgs)
            else:
                bot.channelMsg("Duel error...")
        elif defenderRoll > attackerRoll:
            winnerMsgArgs = (otherUserTry, attackerRoll, user, defenderRoll, user, duelData["amount"]*2, config.currencyPlural)
            bot.channelMsg("KevinTurtle KevinTurtle KevinTurtle | %s rolled a %d and %s rolled a %d. %s wins the %d %s! | KevinTurtle KevinTurtle KevinTurtle" % winnerMsgArgs)
            loserBalArgs = (otherUserData["balance"] - duelData["amount"], timeNow, otherUserData["duel_profit"] - duelData["amount"], otherUserTry, otherUserData["balance"])
            if bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ?, duels_lost = duels_lost + 1, duel_profit = ? WHERE twitchname = ? AND balance = ?", loserBalArgs) == 1:
                winnerBalArgs = (userData["balance"] + duelData["amount"], timeNow, userData["duel_profit"] + duelData["amount"], user, userData["balance"])
                bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ?, duels_won = duels_won + 1, duel_profit = ? WHERE twitchname = ? AND balance = ?", winnerBalArgs)
                bot.updateHighestBalance(userData, userData["balance"]+duelData["amount"])
                resultLogArgs = (otherUserTry, user, attackerRoll, defenderRoll, duelData["amount"], user, timeNow, bot.factory.channel)
                bot.execQueryModify("INSERT INTO duel_results (from_user, to_user, roll1, roll2, amount, winner, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", resultLogArgs)
            else:
                bot.channelMsg("Duel error...")
        else:
            winnerMsgArgs = (otherUserTry, attackerRoll, user, defenderRoll)
            bot.channelMsg("KevinTurtle KevinTurtle KevinTurtle | %s rolled a %d and %s rolled a %d. Draw! No-one gains or loses anything. | KevinTurtle KevinTurtle KevinTurtle" % winnerMsgArgs)
            resultLogArgs = (otherUserTry, user, attackerRoll, defenderRoll, duelData["amount"], timeNow, bot.factory.channel)
            bot.execQueryModify("INSERT INTO duel_results (from_user, to_user, roll1, roll2, amount, whenHappened, channel) VALUES(?, ?, ?, ?, ?, ?, ?)", resultLogArgs)
            bot.execQueryModify("UPDATE users SET last_activity = ?, duels_tied = duels_tied + 1 WHERE twitchname IN(?, ?)", (timeNow, otherUserTry, user))
            
        # done!
        bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
    
    elif arglist[0] == "reject":
        if len(arglist) < 2:
            bot.addressUser(user, "You didn't specify a user to reject the challenge from.")
            return
        
        otherUserTry = arglist[1]
        # check duels
        duelData = bot.execQuerySelectOne("SELECT * FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
        
        if duelData == None:
            bot.addressUser(user, "You don't have a pending challenge from %s. Use %sduel list to check your pending challenges." % (otherUserTry, config.cmdChar))
            return
        
        bot.addressUser(otherUserTry, "%s rejected your duel request." % user)
        bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
    
    else:
        bot.addressUser(user, "See %scommands to get the list of things you can do with %sduel." % (config.cmdChar, config.cmdChar))
        return
        
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return False

