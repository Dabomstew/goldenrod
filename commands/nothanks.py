import goldenrod
import datetime, time

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "broadcaster"):
        return
    bot.execQueryModify("UPDATE channels SET joinIfLive = ?, lastChange = ? WHERE channel = ?", (False, int(time.time()), bot.factory.channel))
    goldenrod.leaveChannel(bot.factory.channel, "Leaving at broadcaster's request, bye all!")
    
def requiredPerm():
    return "broadcaster"
    
def canUseByWhisper():
    return False

