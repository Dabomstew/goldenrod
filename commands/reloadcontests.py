def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    if bot.contestManager.currentContest != None:
        bot.channelMsg("Sorry %s, wait until the end of the current contest." % user)
    else:
        bot.contestManager.loadContests()
        bot.channelMsg("Got it %s, reloaded my contests." % user)
    
def requiredPerm():
    return "owner"