import config

def execute(parser, bot, user, args):
    if not args:
        args = user
        
    arglist = args.split()
    balanceCheck = bot.execQuerySelectOne("SELECT COUNT(*) FROM coinflips WHERE twitchname = ? AND winner = ?", (arglist[0].lower(), 0))
    if balanceCheck == None:
        bot.channelMsg("%s -> Invalid argument." % user)
    else:
        loseCount = balanceCheck["COUNT(*)"]
        winCount = bot.execQuerySelectOne("SELECT COUNT(*) FROM coinflips WHERE twitchname = ? AND winner = ?", (arglist[0].lower(), 1))["COUNT(*)"]
        bot.channelMsg("%s -> %s has won coin flips %d times and lost %d times." % (user, arglist[0].lower(), winCount, loseCount))
    
def requiredPerm():
    return "anyone"