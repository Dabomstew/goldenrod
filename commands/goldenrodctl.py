from twisted.internet import reactor
import config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "mod"):
        return
    if not args:
        argument = ""
    else:
        argument = args.split()[0].strip().lower()
    if(argument == "off" and bot.commandsEnabled):
        bot.setCommandsEnabled(False)
        bot.addressUser(user, "Goldenrod turned off. Use %sgoldenrodctl to re-enable." % (config.cmdChar))
    elif(argument != "off" and not bot.commandsEnabled):
        bot.setCommandsEnabled(True)
        bot.addressUser(user, "Goldenrod Gaming enabled! Use %sgoldenrodctl off to turn it off when you want your chat back." % (config.cmdChar))
    else:
        bot.addressUser(user, "Goldenrod is currently %s." % ("on" if bot.commandsEnabled else "off"))
    
def requiredPerm():
    return "mod"
    
def canUseByWhisper():
    return False

