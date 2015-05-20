from twisted.internet import reactor
import config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "broadcaster") and not parser.checkPerms(bot, user, "owner"):
        return
    if not args:
        argument = ""
    else:
        argument = args.split()[0].strip().lower()
    if(argument == "off" and bot.commandsEnabled):
        bot.setCommandsEnabled(False)
        bot.channelMsg("%s -> Goldenrod turned off. Use %sgoldenrodctl to re-enable." % (user, config.cmdChar))
    elif(argument != "off" and not bot.commandsEnabled):
        bot.setCommandsEnabled(True)
        bot.channelMsg("%s -> Goldenrod Gaming enabled! Use %sgoldenrodctl off to turn it off when you want your chat back." % (user, config.cmdChar))
    else:
        bot.channelMsg("%s -> Goldenrod is currently %s." % (user, "on" if bot.commandsEnabled else "off"))
    
def requiredPerm():
    return "broadcaster"
    