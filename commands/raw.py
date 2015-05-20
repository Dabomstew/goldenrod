def execute(parser, bot, user, args):
    if not parser.checkPerms(bot, user, "owner"):
        return
    bot.channelMsg(args)

def requiredPerm():
    return "owner"  