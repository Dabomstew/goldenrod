from twisted.internet import reactor
import goldenrod, config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or not bot.isWhisperRequest():
        return
    from goldenrod import channelInstances
    channelsIamIn = "I am in: "
    channelsIamIn += ", ".join(channel for channel in channelInstances)
    bot.addressUser(user, "%s" % channelsIamIn)
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True

