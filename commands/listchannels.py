from twisted.internet import reactor
import goldenrod, config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or (bot.factory.channel != config.botOwner and bot.factory.channel != config.botNick):
        return
    from goldenrod import channelInstances
    channelsIamIn = "I am in: "
    channelsIamIn += ", ".join(channel for channel in channelInstances)
    bot.channelMsg("%s -> %s" % (user, channelsIamIn))
    
def requiredPerm():
    return "owner"