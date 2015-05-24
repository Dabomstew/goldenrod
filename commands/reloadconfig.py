import config

def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    reload(config)
    bot.channelMsg("Got it %s, reloaded my config." % user)
    
def requiredPerm():
    return "owner"