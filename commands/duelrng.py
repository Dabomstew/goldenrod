import config

def execute(parser, bot, user, args):
    if not args:
        args = user
        
    arglist = args.split()
    balanceCheck = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (arglist[0].lower(),))
    if balanceCheck == None:
        bot.addressUser(user, "%s hasn't played on Goldenrod yet." % (arglist[0].lower()))
    else:
        msgArgs = (arglist[0].lower(), balanceCheck["duels_won"], balanceCheck["duels_lost"], balanceCheck["duels_tied"], balanceCheck["duel_profit"], config.currencyPlural)
        bot.addressUser(user, "%s has won %d duels and lost %d with %d ties. Their overall profit/loss from duels is %d %s." % msgArgs)
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

