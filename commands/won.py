import config

def execute(parser, bot, user, args):
    if not args:
        args = user
    arglist = args.split()
    balanceCheck = bot.execQuerySelectOne("SELECT SUM(amount) AS pointsLost FROM coinflips WHERE winner = 1 AND twitchname = ?", (arglist[0].lower(),))
    if balanceCheck == None or balanceCheck["pointsLost"] == None:
        bot.channelMsg("%s -> %s hasn't won any coin flips." % (user, arglist[0].lower()))
    else:
        bot.channelMsg(("%s -> %s has won %d %s from coin flips." % (user, arglist[0].lower(), balanceCheck["pointsLost"], config.currencyPlural)))
    
def requiredPerm():
    return "anyone"