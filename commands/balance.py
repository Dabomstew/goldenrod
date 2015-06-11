import config

def execute(parser, bot, user, args):
    if not args:
        bot.addressUser(user, "Your balance is %d %s." % (bot.getUserDetails(user)["balance"], config.currencyPlural))
    else:
        arglist = args.split()
        balanceCheck = bot.execQuerySelectOne("SELECT * FROM users WHERE twitchname = ?", (arglist[0].lower(),))
        if balanceCheck == None:
            bot.addressUser(user, "Your balance is %d %s." % (bot.getUserDetails(user)["balance"], config.currencyPlural))
        else:
            bot.addressUser(user, ("%s's balance is %d %s." % (balanceCheck["twitchname"], balanceCheck["balance"], config.currencyPlural)).encode("utf-8"))
            
        if arglist[0].lower() == config.botOwner and not bot.isWhisperRequest():
            bot.channelMsg("/me DansGame H A X DansGame")
    
def requiredPerm():
    return "anyone"
    
def canUseByWhisper():
    return True

