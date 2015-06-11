import config

def execute(parser, bot, user, args):
    if not args:
        args = user
        
    arglist = args.split()
    balanceCheck = bot.execQuerySelectOne("SELECT COALESCE(ROUND(1.0*SUM(amount)/COUNT(*), 5), 0) AS averageHandout, COUNT(*) as handCount FROM handouts WHERE twitchname = ?", (arglist[0].lower(),))
    if balanceCheck == None:
        bot.addressUser(user, "Invalid argument.")
    else:
        bot.addressUser(user, "%s has begged for %d handouts and received an average of %.05f %s per handout." % (arglist[0].lower(), balanceCheck["handCount"], balanceCheck["averageHandout"], config.currencyPlural))
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

