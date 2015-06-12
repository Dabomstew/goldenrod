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
        bot.addressUser(user, "Goldenrod turned off. Use %sgoldenrodctl on or %sgoldenrodctl quiet to re-enable." % (config.cmdChar, config.cmdChar))
    elif(argument == "quiet" and not bot.inQuietMode):
        bot.setCommandsEnabled(True)
        bot.setQuietMode(True)
        bot.addressUser(user, "Goldenrod Gaming shifted to quiet mode! Spammy commands like %shandout are disabled." % (config.cmdChar))
    elif(argument == "on" and (not bot.commandsEnabled or bot.inQuietMode)):
        bot.setCommandsEnabled(True)
        bot.setQuietMode(False)
        bot.addressUser(user, "Goldenrod Gaming turned on fully! Spammy commands like %shandout are enabled." % (config.cmdChar))
    else:
        if bot.commandsEnabled:
            if bot.inQuietMode:
                bot.addressUser(user, "Goldenrod is currently on in quiet mode.")
            else:
                bot.addressUser(user, "Goldenrod is currently on in normal mode.")
        else:
            bot.addressUser(user, "Goldenrod is currently off.")
    
def requiredPerm():
    return "mod"
    
def canUseByWhisper():
    return False

