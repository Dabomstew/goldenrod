from config import botOwner
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import glob, importlib
import commands
import os.path

class CommandParser:

    def __init__(self):
        self.commandMethods = {}
        self.allImportedModules = {}
        self.importedModuleMTimes = {}
        
    def loadCommands(self):
        # command files
        self.commandMethods = {}
        methodFiles = glob.glob("./commands/*.py")
        for methodFile in methodFiles:
            if "\\" in methodFile:
                cmdName = methodFile[methodFile.rfind('\\')+1:methodFile.rfind('.')]
            else:
                cmdName = methodFile[methodFile.rfind('/')+1:methodFile.rfind('.')]
            if cmdName == "__init__":
                continue
            if cmdName in self.allImportedModules:
                cmdModule = self.allImportedModules[cmdName]
                newMTime = os.path.getmtime(methodFile)
                if newMTime > self.importedModuleMTimes[cmdName]:
                    cmdModule = reload(cmdModule)
                    self.allImportedModules[cmdName] = cmdModule
                    self.importedModuleMTimes[cmdName] = newMTime
            else:
                cmdModule = importlib.import_module("commands.%s" % cmdName)
                self.allImportedModules[cmdName] = cmdModule
                self.importedModuleMTimes[cmdName] = os.path.getmtime(methodFile)
            self.commandMethods[cmdName] = cmdModule
    
    def saveCommands(self):
        # do nothing
        return  
    
    def parse(self, bot, user, command, args, fromWhisperer):
        # parse it lol
        command = command.lower()
        args = args.strip()
        if command in self.commandMethods and (not fromWhisperer or self.commandMethods[command].canUseByWhisper()):
            if self.checkPerms(bot, user, self.commandMethods[command].requiredPerm()):
                self.commandMethods[command].execute(self, bot, user, args)
        
    def purgeise(self, str):
        universion = str.decode('utf-8')
        newstr = u""
        ind = 0
        lencheck = len(universion)
        for c in universion:
            cnum = ord(c)
            if cnum >= 0x21 and cnum <= 0x7E:
                cnum += 0xFEE0
            elif cnum == 0x20:
                cnum = 0x3000
            newstr += unichr(cnum)
            if ind != lencheck-1:
                newstr += unichr(0x20)
            ind += 1
        return newstr.encode('utf-8')
        
    
    def checkPerms(self, bot, user, perm):
        if perm == "owner" and user == botOwner:
            return True
        elif perm == "broadcaster" and user == bot.factory.channel:
            return True
        elif perm == "mod" and (user in bot.channelMods or user == botOwner or user == bot.factory.channel):
            return True
        elif perm == "anyone" or perm == "":
            return True
        else:
            return False