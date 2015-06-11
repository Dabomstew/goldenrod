from twisted.internet import reactor
import goldenrod, config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or not bot.isWhisperRequest():
        return
    commandBits = args.split(' ', 1)
    if len(commandBits) < 2:
        bot.addressUser(user, "Invalid arguments.")
        return
    farChannel = commandBits[0].strip().lower()
    message = commandBits[1].strip()
    from goldenrod import channelInstances
    if farChannel not in channelInstances:
        return
    channelInstances[farChannel].privmsg("%s!" % user, "#%s" % farChannel, message)
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True

