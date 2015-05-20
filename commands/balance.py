import config

def execute(parser, bot, user, args):
    if not args:
        bot.channelMsg("%s -> Your balance is %d %s." % (user, bot.getUserDetails(user)["balance"], config.currencyPlural))
    else:
        arglist = args.split()
        balanceCheck = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (arglist[0].lower(),))
        if balanceCheck == None:
            bot.channelMsg("%s -> Your balance is %d %s." % (user, bot.getUserDetails(user)["balance"], config.currencyPlural))
        else:
            bot.channelMsg(("%s -> %s's balance is %d %s." % (user, balanceCheck["twitchname"], balanceCheck["balance"], config.currencyPlural)).encode("utf-8"))
    
def requiredPerm():
    return "anyone"