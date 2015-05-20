def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    parser.loadCommands()
    bot.channelMsg("Got it %s, reloaded my commands." % user)
    
def requiredPerm():
    return "owner"