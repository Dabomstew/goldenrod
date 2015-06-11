def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    bot.channelMsg(".mods")
        
def requiredPerm():
    return "owner"
    
def canUseByWhisper():
    return False

