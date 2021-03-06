import goldenrod, time, threading

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "broadcaster"):
        return
    sleeptime = 0
    try:
        sleeptime = int(args)
    except ValueError:
        bot.addressUser(user, "Invalid argument.")
        return
    if sleeptime < 1 or sleeptime > 1440:
        bot.addressUser(user, "Cannot silence for no time or more than 1 day. Try !nothanks instead if you want the bot gone.")
        return
    bot.addressUser(user, "Commands disabled for %d minutes." % sleeptime)
    bot.acceptCommands = False
    resThread = threading.Thread(target=returnCommands, args=(sleeptime, bot))
    resThread.daemon = True
    resThread.start()

def returnCommands(sleeptime, bot):
    time.sleep(sleeptime*60)
    bot.acceptCommands = True
    
def requiredPerm():
    return "broadcaster"
    
def canUseByWhisper():
    return False

