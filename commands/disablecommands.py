from twisted.internet import reactor
import goldenrod
import config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or bot.factory.channel != config.botNick:
        return
    newChannel = args.split()[0].strip().lower()
    if newChannel == "":
        return
    goldenrod.removeFromCommandsEnabled(newChannel)
    bot.channelMsg("%s -> Disabled commands on %s." % (user, newChannel))
    
def requiredPerm():
    return "owner"
    