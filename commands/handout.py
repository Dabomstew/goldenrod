# coding=utf-8

import config
import random
import datetime, time
import math
from twisted.internet import reactor
from collections import OrderedDict

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
    
def romannumerals(number): 
    romanrep = ""
    
    numthousands = number / 1000
    number %= 1000
    romanrep += "M"*numthousands
    
    if number >= 900:
        number -= 900
        romanrep += "CM"
    elif number >= 500:
        numhundreds = (number-500)/100
        number %= 100
        romanrep += "D" + ("C" * numhundreds)
    elif number >= 400:
        number -= 400
        romanrep += "CD"
    elif number >= 100:
        numhundreds = number/100
        number %= 100
        romanrep += "C" * numhundreds
        
    if number >= 90:
        number -= 90
        romanrep += "XC"
    elif number >= 50:
        numtens = (number-50)/10
        number %= 10
        romanrep += "L" + ("X" * numtens)
    elif number >= 40:
        number -= 40
        romanrep += "XL"
    elif number >= 10:
        numtens = number/10
        number %= 10
        romanrep += "X" * numtens
        
    if number >= 9:
        romanrep += "IX"
    elif number >= 5:
        numones = number-5
        romanrep += "V" + ("I" * numones)
    elif number >= 4:
        romanrep += "IV"
    elif number >= 1:
        romanrep += "I" * number
        
    return thinpurgeise(romanrep)
    
def circlenumber(number):
    if number >= 1 and number <= 20:
        return unichr(0x245F + number).encode("utf-8")
        
    circlerep = ""
    decplace = 1
    
    while number >= decplace:
        thisplace = (number / decplace) % (decplace * 10)
        if thisplace == 0:
            circlerep = unichr(0x24EA).encode("utf-8") + circlerep
        else:
            circlerep = unichr(thisplace+0x245F).encode("utf-8") + circlerep
        decplace *= 10
    
    return circlerep
    
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
    if bot.inQuietMode:
        bot.tellAboutQuietMode(user)
        return
        
    argslow = args.lower().strip()
    
    if config.botOwner in argslow:
        bot.addressUser(user, "How cute, you think begging the owner is actually going to work.")
        return
    
    saidPlease = False
    words = argslow.split()
    magicword = None
    if len(words) >= 1:
        magicword = words[0]
        for keyword in config.magicWords:
            if keyword == words[0]:
                saidPlease = True
        
    if not magicword:
        magicword = None
    else:
        magicword = magicword.decode("utf-8")
        if len(magicword) > 32:
            magicword = magicword[0:32]   

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
                    bot.addressUser(user, "You're either scripting handouts or need to ease up on the manual handout timing. Take a break from them for 1 hour.")
                    bot.execQueryModify("UPDATE users SET handout_ban = ? WHERE twitchname = ?", (bannedUntil, user))
                    return
                    
            if len(diffs) >= 30:
                midTermSDev = handoutsdev(diffs, 30)
                if midTermSDev < 3:
                    bannedUntil = timeNow + config.handoutScriptBan
                    bot.addressUser(user, "You're either scripting handouts or need to ease up on the manual handout timing. Take a break from them for 1 hour.")
                    bot.execQueryModify("UPDATE users SET handout_ban = ? WHERE twitchname = ?", (bannedUntil, user))
                    return
                    
            if len(diffs) >= 50:
                longTermSDev = handoutsdev(diffs, 50)
                if longTermSDev < 8:
                    bannedUntil = timeNow + config.handoutScriptBan
                    bot.addressUser(user, "You're either scripting handouts or need to ease up on the manual handout timing. Take a break from them for 1 hour.")
                    bot.execQueryModify("UPDATE users SET handout_ban = ? WHERE twitchname = ?", (bannedUntil, user))
                    return
        # success
        handout = 0
        while True:
            doContinue = False
            if handout >= 10:
                randRoll = random.randint(0, 10)
                doContinue = (randRoll == 10) or (random.randint(1, 100) == 1) # preserve 1/10 chance of continuing [1/11 + 10/11*1/100]
            else:
                randRoll = random.randint(1, 10)
                doContinue = (randRoll == 10)
            
            if saidPlease:
                randRoll = max(randRoll, random.randint(0, 8))
            
            if doContinue:
                handout = handout + 10
            else:
                handout = handout + randRoll
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
        logArgs = (user, handout, timeNow, bot.factory.channel, magicword)
        bot.execQueryModify("INSERT INTO handouts (twitchname, amount, whenHappened, channel, magicWord) VALUES(?, ?, ?, ?, ?)", logArgs)
        
        bot.addressUser(user, random.choice(handoutMessages))
        
        if handout > 60:
            bot.channelMsg("Congratulations %s! You should probably go buy a lottery ticket..." % user)
        elif handout > 50:
            bot.channelMsg("Well done, %s! 50 points! Just think of how many you could have had if you won 16 yolocoins in a row instead..." % user)
        elif handout > 40:
            bot.channelMsg("40 points, not bad at all %s. But would you have preferred to use that luck on a shiny?" % user)
    else:
        reactor.whisperer.sendWhisper(user, "On cooldown. (%d secs)" % canPlay)
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return False

