from twisted.internet import reactor
import goldenrod, config
import datetime

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or bot.factory.channel != config.botNick:
        return
    newChannel = args.split()[0].strip().lower()
    if newChannel == "":
        return
    channelDataCheck = bot.execQuerySelectOne("SELECT * FROM channels WHERE channel = ?", (newChannel,))
    if channelDataCheck == None:
        bot.execQueryModify("INSERT INTO channels (channel, commandsEnabled, lastChange, joinIfLive) VALUES(?, ?, ?, ?)", (newChannel, True, datetime.datetime.now(), True))
    else:
        bot.execQueryModify("UPDATE channels SET joinIfLive = ?, lastChange = ? WHERE channel = ?", (True, datetime.datetime.now(), newChannel))
    bot.channelMsg("%s -> Set channel %s to be joined when live." % (user, newChannel))
    
def requiredPerm():
    return "owner"
    