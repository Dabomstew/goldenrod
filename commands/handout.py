# coding=utf-8

import config
import random
import datetime, time
import math

def thinpurgeise(str):
    universion = str.decode('utf-8')
    newstr = u""
    ind = 0
    lencheck = len(universion)
    for c in universion:
        cnum = ord(c)
        if cnum >= 0x21 and cnum <= 0x7E:
            cnum += 0xFEE0
        elif cnum == 0x20:
            cnum = 0x3000
        newstr += unichr(cnum)
        ind += 1
    return newstr.encode('utf-8')
    
def handoutsdev(diffs, number):
    meantotal = 0
    for i in xrange(0, number):
        meantotal += diffs[i]
        
    meantotal = meantotal/float(number)
    vartotal = 0.0
    
    for i in xrange(0, number):
        vartotal += (diffs[i] - meantotal) ** 2
        
    sdev = math.sqrt(vartotal/float(number))
    return sdev
    
def execute(parser, bot, user, args):
    argslow = args.lower().strip()
    
    saidPlease = False
    for keyword in config.magicWords:
        if keyword in argslow:
            saidPlease = True
    
    userData = bot.getUserDetails(user)
    
    timeNow = int(time.time())
    if userData["handout_ban"] > timeNow:
        return
    canPlay = bot.canPlayGame(userData)
    if canPlay == 0:
        # let's look at sdevs
        listOfHandouts = bot.execQuerySelectMultiple("SELECT * FROM handouts WHERE twitchname = ? ORDER BY rowid DESC LIMIT 50", (user,))
        if len(listOfHandouts) >= 10:
            timestamps = []
            timestamps.append(float(timeNow - 1430000000))
            for handoutRow in listOfHandouts:
                thistime = handoutRow["whenHappened"]
                timestamps.append(float(thistime - 1430000000))
            
            diffs = []
            for i in xrange(0, len(timestamps)-1):
                thisdiff = timestamps[i] - timestamps[i+1]
                diffs.append(thisdiff)
                
            if len(diffs) >= 10:
                shortTermSDev = handoutsdev(diffs, 10)
                if shortTermSDev < 1:
                    bannedUntil = timeNow + config.handoutScriptBan
                    bot.channelMsg("%s -> You're either scripting handouts or need to ease up on the manual handout timing. Take a break from them for 1 hour." % user)
                    bot.execQueryModify("UPDATE users SET handout_ban = ? WHERE twitchname = ?", (bannedUntil, user))
                    return
                    
            if len(diffs) >= 30:
                midTermSDev = handoutsdev(diffs, 30)
                if midTermSDev < 3:
                    bannedUntil = timeNow + config.handoutScriptBan
                    bot.channelMsg("%s -> You're either scripting handouts or need to ease up on the manual handout timing. Take a break from them for 1 hour." % user)
                    bot.execQueryModify("UPDATE users SET handout_ban = ? WHERE twitchname = ?", (bannedUntil, user))
                    return
                    
            if len(diffs) >= 50:
                longTermSDev = handoutsdev(diffs, 50)
                if longTermSDev < 8:
                    bannedUntil = timeNow + config.handoutScriptBan
                    bot.channelMsg("%s -> You're either scripting handouts or need to ease up on the manual handout timing. Take a break from them for 1 hour." % user)
                    bot.execQueryModify("UPDATE users SET handout_ban = ? WHERE twitchname = ?", (bannedUntil, user))
                    return
        # success
        handout = 0
        while True:
            if saidPlease:
                randRoll = max(random.randint(1, 10), random.randint(1, 7))
            else:
                randRoll = random.randint(1, 10)
            handout = handout + randRoll
            if randRoll != 10:
                break
                
        currencyNow = config.currencyName if (handout == 1) else config.currencyPlural
        if random.randint(1, 256) == 256:
            handout = 0
            handoutMessages = ["Error 404, points not found. Perhaps next time?", "Oops, I slipped and dropped my wallet full of points so I can't help you. Try again later.", "SYSTEM used PAY DAY! SYSTEM's attack missed!"]
        elif userData["balance"] > 0:
            handoutMessages = ["Here, take %d %s." % (handout, currencyNow), "If I give you %d %s will you leave me alone?" % (handout, currencyNow), "Fine. %d %s for you. Now shoo!" % (handout, currencyNow), "I'm actually feeling pretty generous today, so have %d %s." % (handout, currencyNow), "I-It's not like I wanted to give you %d %s or anything! B-Baka!" % (handout, currencyNow), "I present %d %s to Mr. Beggar Extraordinaire over here." % (handout, currencyNow), "I present %d %s to Ms. Beggar Extraordinaire over here." % (handout, currencyNow), "The Goldenrod Gods have spoken. Thou shalt receive %d %s." % (handout, currencyNow), "The hammer has deemed you not worthy. Here is your consolation prize of %d %s." % (handout, currencyNow), "I'll allow you to take %d %s off my hands if you promise not to tell anyone." % (handout, currencyNow), "%s grew to level %d! %s gained %d %s!" % (user, userData["handouts"]+1, user, handout, currencyNow), thinpurgeise("Up Down Left Right %d %s A B Start Select" % (handout, currencyNow)), "You just passed GO! Take %d %s." % (handout, currencyNow), "On coold- HEY! What's the meaning of stealing %d %s from me? Oh well, I may as well let you have them...ᴡᴀᴛᴄʜ ʏᴏᴜʀ ʙᴀᴄᴋ..." % (handout, currencyNow)]
        else:
            handoutMessages = ["You irresponsible gambler, how dare you waste my generosity. But I feel obligated to get you back on your feet again, so here's %d %s." % (handout, currencyNow), "Another yolocoiner? The line's over there... Fine, have %d %s but get out of my sight." % (handout, currencyNow)]
            
        newHighest = max(userData["highest_handout"], handout)
        queryArgs = (userData["balance"]+handout, timeNow, timeNow, newHighest, user, userData["balance"])
        bot.execQueryModify("UPDATE users SET balance = ?, last_game = ?, last_activity = ?, handouts = handouts + 1, highest_handout = ? WHERE twitchname = ? AND balance = ?", queryArgs)
        bot.updateHighestBalance(userData, userData["balance"]+handout)
        logArgs = (user, handout, timeNow, bot.factory.channel)
        bot.execQueryModify("INSERT INTO handouts (twitchname, amount, whenHappened, channel) VALUES(?, ?, ?, ?)", logArgs)
        
        bot.channelMsg("%s -> %s" % (user, random.choice(handoutMessages)))
        
        if handout > 60:
            bot.channelMsg("Congratulations %s! You should probably go buy a lottery ticket..." % user)
        elif handout > 50:
            bot.channelMsg("Well done, %s! 50 points! Just think of how many you could have had if you won 16 yolocoins in a row instead..." % user)
        elif handout > 40:
            bot.channelMsg("40 points, not bad at all %s. But would you have preferred to use that luck on a shiny?" % user)
    else:
        if config.showCooldowns:
            bot.channelMsg("%s -> On cooldown. (%d secs)" % (user, canPlay))
    
def requiredPerm():
    return "anyone"