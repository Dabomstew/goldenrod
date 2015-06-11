def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    parser.loadCommands()
    bot.addressUser(user, "Got it, reloaded my commands.")
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True

