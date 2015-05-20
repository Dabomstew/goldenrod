import config
import random
import datetime, time
import math

def execute(parser, bot, user, args):
    argslow = args.lower().strip()
    # saidPlease = argslow.startswith("please") or argslow.startswith("pls") or argslow.startswith("plz")
    saidPlease = False # lol
    userData = bot.getUserDetails(user)
    
    timeNow = int(time.time())
    if userData["handout_ban"] > timeNow:
        return
    canPlay = bot.canPlayGame(userData)
    if canPlay == 0:
        # let's look at sdevs
        listOfHandouts = bot.execQuerySelectMultiple("SELECT * FROM handouts WHERE twitchname = ? ORDER BY rowid DESC LIMIT 10", (user,))
        if len(listOfHandouts) == 10:
            meantotal = 0.0
            timestamps = []
            timestamps.append(float(timeNow - 1430000000))
            for handoutRow in listOfHandouts:
                thistime = time.mktime(time.strptime(handoutRow["whenHappened"].encode("utf-8").split(".")[0], "%Y-%m-%d %H:%M:%S"))
                timestamps.append(float(thistime - 1430000000))
            
            diffs = []
            for i in xrange(0, 10):
                thisdiff = timestamps[i] - timestamps[i+1]
                diffs.append(thisdiff)
                meantotal += (thisdiff)
                
            meantotal = meantotal/10.0
            vartotal = 0.0
            for diffval in diffs:
                vartotal += (diffval - meantotal)*(diffval - meantotal)
            sdevtotal = math.sqrt(vartotal/10.0)
            print "sdev=", sdevtotal
            if sdevtotal < 1.3:
                bannedUntil = timeNow + config.handoutScriptBan
                bot.channelMsg("%s -> stop scripting! (banned from handouts for 1 hour)" % user)
                bot.execQueryModify("UPDATE users SET handout_ban = ? WHERE twitchname = ?", (bannedUntil, user))
                return
        # success
        handout = 0
        while True:
            if saidPlease:
                randRoll = random.randint(2, 10)
            else:
                randRoll = random.randint(1, 10)
            handout = handout + randRoll
            if randRoll != 10:
                break
        
        newHighest = max(userData["highest_handout"], handout)
        queryArgs = (userData["balance"]+handout, timeNow, datetime.datetime.now(), newHighest, user, userData["balance"])
        bot.execQueryModify("UPDATE users SET balance = ?, last_game = ?, last_activity = ?, handouts = handouts + 1, highest_handout = ? WHERE twitchname = ? AND balance = ?", queryArgs)
        bot.updateHighestBalance(userData, userData["balance"]+handout)
        logArgs = (user, handout, datetime.datetime.now())
        bot.execQueryModify("INSERT INTO handouts (twitchname, amount, whenHappened) VALUES(?, ?, ?)", logArgs)
        currencyNow = config.currencyName if (handout == 1) else config.currencyPlural
        if userData["balance"] > 0:
            handoutMessages = ["Here, take %d %s." % (handout, currencyNow), "If I give you %d %s will you leave me alone?" % (handout, currencyNow), "Fine. %d %s for you. Now shoo!" % (handout, currencyNow), "I'm actually feeling pretty generous today, so have %d %s." % (handout, currencyNow), "I-It's not like I wanted to give you %d %s or anything! B-Baka!" % (handout, currencyNow), "I present %d %s to Mr. Beggar Extraordinaire over here." % (handout, currencyNow), "I present %d %s to Ms. Beggar Extraordinaire over here." % (handout, currencyNow), "The Goldenrod Gods have spoken. Thou shalt receive %d %s." % (handout, currencyNow)]
        else:
            handoutMessages = ["You irresponsible gambler, how dare you waste my generosity. But I feel obligated to get you back on your feet again, so here's %d %s." % (handout, currencyNow)]
        
        bot.channelMsg("%s -> %s" % (user, handoutMessages[random.randint(0, len(handoutMessages)-1)]))
    else:
        if config.showCooldowns:
            bot.channelMsg("%s -> On cooldown. (%d secs)" % (user, canPlay))
    
def requiredPerm():
    return "anyone"