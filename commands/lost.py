import config

def execute(parser, bot, user, args):
    if not args:
        args = user
    arglist = args.split()
    balanceCheck = bot.execQuerySelectOne("SELECT SUM(amount) AS pointsLost FROM coinflips WHERE winner = 0 AND twitchname = ?", (arglist[0].lower(),))
    if balanceCheck == None or balanceCheck["pointsLost"] == None:
        bot.addressUser(user, "%s hasn't lost any coin flips." % arglist[0].lower())
    else:
        bot.addressUser(user, "%s has lost %d %s to coin flips." % (arglist[0].lower(), balanceCheck["pointsLost"], config.currencyPlural))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

