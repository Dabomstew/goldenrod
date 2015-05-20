from twisted.internet import reactor
import goldenrod, config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or (bot.factory.channel != config.botOwner and bot.factory.channel != config.botNick):
        return
    commandBits = args.split(' ', 1)
    if len(commandBits) < 2:
        bot.channelMsg("%s -> Invalid arguments." % (user))
        return
    farChannel = commandBits[0].strip().lower()
    message = commandBits[1].strip()
    from goldenrod import channelInstances
    if farChannel not in channelInstances:
        return
    channelInstances[farChannel].channelMsg(message)
    
def requiredPerm():
    return "owner"