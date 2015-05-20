from twisted.internet import reactor
import goldenrod, config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner") or bot.factory.channel != config.botNick:
        return
    newChannel = args.split()[0].strip().lower()
    if newChannel == "":
        return
    goldenrod.addToCommandsEnabled(newChannel)
    bot.channelMsg("%s -> Enabled commands on %s." % (user, newChannel))
    
def requiredPerm():
    return "owner"
    