import config
import random
import datetime, time
import math

def execute(parser, bot, user, args):
    if "bot" in user:
        bot.channelMsg("%s -> LOL nope." % user)
        return
        
    altCheck = bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (user,))
    
    if altCheck != None:
        bot.channelMsg("%s -> Known alts aren't allowed to participate in duels." % user)
        return
        
    userData = bot.getUserDetails(user)
    timeNow = int(time.time())
    
    if args == None or args.strip() == "":
        bot.channelMsg("%s -> See %scommands to get the list of things you can do with %sduel." % (user, config.cmdChar, config.cmdChar))
        return
        
    bot.execQueryModify("DELETE FROM duel_requests WHERE expiry <= ?", (timeNow,))
    arglist = args.lower().split()
    if arglist[0] != "list" and arglist[0] != "challenge" and arglist[0] != "accept" and arglist[0] != "reject":
        arglist = ["challenge"] + arglist
        
    if arglist[0] == "list":
        # check duels
        myDuels = bot.execQuerySelectMultiple("SELECT * FROM duel_requests WHERE to_user = ? ORDER BY whenHappened ASC", (user,))
        if len(myDuels) == 0:
            bot.channelMsg("%s -> You have no pending duel challenges." % user)
        else:
            finalMessage = "%s -> You have %d pending duel challenges: " % (user, len(myDuels))
            for duel in myDuels:
                finalMessage = "%s%s - %d %s, " % (finalMessage, duel["from_user"], duel["amount"], config.currencyName if (duel["amount"] == 1) else config.currencyPlural)
            
            finalMessage = finalMessage[:-2]
            bot.channelMsg(finalMessage.encode("utf-8"))
            
    elif arglist[0] == "challenge":
        # challenges are on cooldown
        canPlay = bot.canPlayGame(userData)
        if canPlay == 0:
            # do shit
            if len(arglist) < 3:
                bot.channelMsg("%s -> Invalid challenge (use %sduel challenge user amount)" % (user, config.cmdChar))
                return
            try:
                amount = int(arglist[2])
            except ValueError:
                bot.channelMsg("%s -> Invalid amount to challenge for." % user)
                return
            if amount <= 0 or amount > userData["balance"]:
                bot.channelMsg("%s -> Invalid amount to challenge for." % user)
                return
            otherUserTry = arglist[1]
            if "bot" in otherUserTry:
                bot.channelMsg("%s -> You can't challenge bots." % user)
                return
            if otherUserTry == user:
                bot.channelMsg("%s -> You can't challenge yourself." % user)
                return
            if otherUserTry in user or user in otherUserTry:
                bot.channelMsg("%s -> Try harder please." % user)
                return
            otherAltCheck = bot.execQuerySelectOne("SELECT * FROM alts WHERE twitchname = ?", (otherUserTry,))
    
            if otherAltCheck != None:
                bot.channelMsg("%s -> You can't challenge a known alt to a duel." % user)
                return
                
            otherUser = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (otherUserTry,))
            if otherUser == None:
                bot.channelMsg("%s -> %s hasn't played on Goldenrod yet." % (user, otherUserTry))
                return
            else:
                if otherUser["balance"] < amount:
                    bot.channelMsg("%s -> %s doesn't have enough %s to accept your challenge." % (user, otherUserTry, config.currencyPlural))
                    return
                    
                otherDuelCheck = bot.execQuerySelectOne("SELECT * FROM duel_requests WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?) LIMIT 1", (user, otherUserTry, otherUserTry, user))
                if otherDuelCheck != None:
                    bot.channelMsg("%s -> There is already a pending duel between you and %s." % (user, otherUserTry))
                    return
                
                # perfect, issue the challenge
                challengeArgs = (user, otherUserTry, amount, timeNow+config.duelRequestExpiry, datetime.datetime.now())
                bot.execQueryModify("INSERT INTO duel_requests (from_user, to_user, amount, expiry, whenHappened) VALUES(?, ?, ?, ?, ?)", challengeArgs)
                # update current user cooldown
                cdArgs = (timeNow, datetime.datetime.now(), user)
                bot.execQueryModify("UPDATE users SET last_game = ?, last_activity = ? WHERE twitchname = ?", cdArgs)
                # acknowledge the request in chat
                bot.channelMsg("%s -> You have issued the %d %s duel request to %s." % (user, amount, config.currencyName, otherUserTry))
                challengerMsgArgs = (otherUserTry, user, amount, config.currencyName if (amount == 1) else config.currencyPlural, config.cmdChar, user, config.cmdChar, user)
                bot.channelMsg("%s -> %s has challenged you to a duel for %d %s! Use %sduel accept %s to accept the request or %sduel reject %s to reject it." % challengerMsgArgs)
                
        else:
            if config.showCooldowns:
                bot.channelMsg("%s -> On cooldown. (%d secs)" % (user, canPlay))
            
    elif arglist[0] == "accept":
        if len(arglist) < 2:
            bot.channelMsg("%s -> You didn't specify a user to accept the challenge from." % user)
            return
        
        otherUserTry = arglist[1]
        # check duels
        duelData = bot.execQuerySelectOne("SELECT * FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
        
        if duelData == None:
            bot.channelMsg("%s -> You don't have a pending challenge from %s. Use %sduel list to check your pending challenges." % (user, otherUserTry, config.cmdChar))
            return
        
        if duelData["amount"] > userData["balance"]:
            bot.channelMsg("%s -> You no longer have enough %s to accept this duel. Rejecting it instead..." % (user, config.currencyPlural))
            bot.channelMsg("%s -> %s was forced to reject your duel request due to not having enough %s left." % (otherUserTry, user, config.currencyPlural))
            bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
            return
        
        otherUserData = bot.getUserDetails(otherUserTry)
        
        if duelData["amount"] > otherUserData["balance"]:
            bot.channelMsg("%s -> %s no longer has enough %s to participate in this duel. Rejecting it automatically..." % (user, otherUserTry, config.currencyPlural))
            bot.channelMsg("%s -> %s was forced to reject your duel request because you no longer have enough %s left." % (otherUserTry, user, config.currencyPlural))
            bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
            return
        
        bot.channelMsg("%s -> %s has accepted your challenge to duel for %d %s. Rolling dice..." % (otherUserTry, user, duelData["amount"], config.currencyName if (duelData["amount"] == 1) else config.currencyPlural))
        attackerRoll = random.randint(1, 6)
        defenderRoll = random.randint(1, 6)
        
        if attackerRoll > defenderRoll:
            winnerMsgArgs = (otherUserTry, attackerRoll, user, defenderRoll, otherUserTry, duelData["amount"]*2, config.currencyPlural)
            bot.channelMsg("KevinTurtle KevinTurtle KevinTurtle | %s rolled a %d and %s rolled a %d. %s wins the %d %s! | KevinTurtle KevinTurtle KevinTurtle" % winnerMsgArgs)
            loserBalArgs = (userData["balance"] - duelData["amount"], datetime.datetime.now(), user, userData["balance"])
            if bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", loserBalArgs) == 1:
                winnerBalArgs = (otherUserData["balance"] + duelData["amount"], datetime.datetime.now(), otherUserTry, otherUserData["balance"])
                bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", winnerBalArgs)
                bot.updateHighestBalance(otherUserData, otherUserData["balance"]+duelData["amount"])
                resultLogArgs = (otherUserTry, user, attackerRoll, defenderRoll, duelData["amount"], otherUserTry, datetime.datetime.now())
                bot.execQueryModify("INSERT INTO duel_results (from_user, to_user, roll1, roll2, amount, winner, whenHappened) VALUES(?, ?, ?, ?, ?, ?, ?)", resultLogArgs)
            else:
                bot.channelMsg("Duel error...")
        elif defenderRoll > attackerRoll:
            winnerMsgArgs = (otherUserTry, attackerRoll, user, defenderRoll, user, duelData["amount"]*2, config.currencyPlural)
            bot.channelMsg("KevinTurtle KevinTurtle KevinTurtle | %s rolled a %d and %s rolled a %d. %s wins the %d %s! | KevinTurtle KevinTurtle KevinTurtle" % winnerMsgArgs)
            loserBalArgs = (otherUserData["balance"] - duelData["amount"], datetime.datetime.now(), otherUserTry, otherUserData["balance"])
            if bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", loserBalArgs) == 1:
                winnerBalArgs = (userData["balance"] + duelData["amount"], datetime.datetime.now(), user, userData["balance"])
                bot.execQueryModify("UPDATE users SET balance = ?, last_activity = ? WHERE twitchname = ? AND balance = ?", winnerBalArgs)
                bot.updateHighestBalance(userData, userData["balance"]+duelData["amount"])
                resultLogArgs = (otherUserTry, user, attackerRoll, defenderRoll, duelData["amount"], user, datetime.datetime.now())
                bot.execQueryModify("INSERT INTO duel_results (from_user, to_user, roll1, roll2, amount, winner, whenHappened) VALUES(?, ?, ?, ?, ?, ?, ?)", resultLogArgs)
            else:
                bot.channelMsg("Duel error...")
        else:
            winnerMsgArgs = (otherUserTry, attackerRoll, user, defenderRoll)
            bot.channelMsg("KevinTurtle KevinTurtle KevinTurtle | %s rolled a %d and %s rolled a %d. Draw! No-one gains or loses anything. | KevinTurtle KevinTurtle KevinTurtle" % winnerMsgArgs)
            resultLogArgs = (otherUserTry, user, attackerRoll, defenderRoll, duelData["amount"], datetime.datetime.now())
            bot.execQueryModify("INSERT INTO duel_results (from_user, to_user, roll1, roll2, amount, whenHappened) VALUES(?, ?, ?, ?, ?, ?)", resultLogArgs)
            
        # done!
        bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
    
    elif arglist[0] == "reject":
        if len(arglist) < 2:
            bot.channelMsg("%s -> You didn't specify a user to reject the challenge from." % user)
            return
        
        otherUserTry = arglist[1]
        # check duels
        duelData = bot.execQuerySelectOne("SELECT * FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
        
        if duelData == None:
            bot.channelMsg("%s -> You don't have a pending challenge from %s. Use %sduel list to check your pending challenges." % (user, otherUserTry, config.cmdChar))
            return
        
        bot.channelMsg("%s -> %s rejected your duel request." % (otherUserTry, user))
        bot.execQueryModify("DELETE FROM duel_requests WHERE from_user = ? AND to_user = ?", (otherUserTry, user))
    
    else:
        bot.channelMsg("%s -> See %scommands to get the list of things you can do with %sduel." % (user, config.cmdChar, config.cmdChar))
        return
        
def requiredPerm():
    return "anyone"