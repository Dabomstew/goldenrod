from twisted.internet import reactor
import goldenrod, config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or not bot.isWhisperRequest():
        return
    newChannel = args.split()[0].strip().lower()
    if newChannel == "":
        return
    goldenrod.addToCommandsEnabled(newChannel)
    bot.addressUser(user, "Enabled commands on %s." % newChannel)
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True


    