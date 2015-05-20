from twisted.internet import reactor
import goldenrod, config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or (bot.factory.channel != config.botOwner and bot.factory.channel != config.botNick):
        return
    from goldenrod import channelInstances
    channelsIamIn = "I am in: "
    for channel in channelInstances:
        channelsIamIn += "%s, " % channel
    bot.channelMsg("%s -> %s" % (user, channelsIamIn[:-2]))
    
def requiredPerm():
    return "owner"