import config

def execute(parser, bot, user, args):
    if not args:
        args = user
    arglist = args.split()
    balanceCheck = bot.execQuerySelectOne("SELECT SUM(amount) AS pointsWon FROM coinflips WHERE winner = 1 AND twitchname = ?", (arglist[0].lower(),))
    if balanceCheck == None or balanceCheck["pointsWon"] == None:
        bot.addressUser(user, "%s hasn't won any coin flips." % arglist[0].lower())
    else:
        bot.addressUser(user, "%s has won %d %s from coin flips." % (arglist[0].lower(), balanceCheck["pointsWon"], config.currencyPlural))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

