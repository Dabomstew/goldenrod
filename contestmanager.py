import glob, importlib
import contests
import time, random, os.path
import config

class ContestManager:

    def __init__(self, bot):
        self.bot = bot
        self.contestModules = {}
        self.allImportedModules = {}
        self.importedModuleMTimes = {}
        self.startNextContest = 0
        self.endCurrentContest = 0
        self.currentContest = None
        
    def loadContests(self):
        # command files
        self.contestModules = {}
        methodFiles = glob.glob("./contests/*.py")
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
                cmdModule = importlib.import_module("contests.%s" % cmdName)
                self.allImportedModules[cmdName] = cmdModule
                self.importedModuleMTimes[cmdName] = os.path.getmtime(methodFile)
            self.contestModules[cmdName] = cmdModule
    
    def unixTimestamp(self):
        return int(time.time())
            
    def run(self):
        self.loadContests()
        self.startNextContest = self.unixTimestamp()+30
        while True:
            time.sleep(1)
            if self.bot.factory.killBot:
                break
            if self.bot.commandsEnabled:
                currtime = self.unixTimestamp()
                if self.currentContest == None and currtime >= self.startNextContest and self.bot.contestsEnabled:
                    self.startAContest()
                
                if self.currentContest != None and self.endCurrentContest != 0 and currtime >= self.endCurrentContest:
                    self.currentContest.end()
                    self.currentContest = None

    def startAContest(self):
        chosen = random.randint(1, 100)
        cumuProb = 0
        for contestEntry in config.contestChoiceWeightings:
            contestName = contestEntry[0]
            contestProb = contestEntry[1]
            if chosen > cumuProb and chosen <= cumuProb + contestProb:
                # chosen this game
                self.currentContest = self.contestModules[contestName].Game(self)
                self.currentContest.start()
                currtime = self.unixTimestamp()
                interval = config.contestInterval
                self.startNextContest = currtime + interval + random.randint(-interval/10, interval/10)
                duration = config.contestDurations[contestName]
                self.endCurrentContest = currtime + duration
                return
            else:
                # nope, check the others
                cumuProb = cumuProb + contestProb
    
    def contestIsDone(self):
        # to be called by the contest itself if someone wins it
        self.currentContest = None