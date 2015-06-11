def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    if bot.contestManager.currentContest != None:
        bot.addressUser(user, "Sorry, wait until the end of the current contest.")
    else:
        bot.contestManager.loadContests()
        bot.addressUser(user, "Got it, reloaded my contests.")
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return False

