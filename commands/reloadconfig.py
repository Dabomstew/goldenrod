import config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    reload(config)
    bot.addressUser(user, "Got it, reloaded my config.")
    
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return True

