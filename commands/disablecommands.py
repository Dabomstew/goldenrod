from twisted.internet import reactor
import goldenrod
import config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or not bot.isWhisperRequest():
        return
    newChannel = args.split()[0].strip().lower()
    if newChannel == "":
        return
    goldenrod.removeFromCommandsEnabled(newChannel)
    bot.addressUser(user, "Disabled commands on %s." % newChannel)
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True


    