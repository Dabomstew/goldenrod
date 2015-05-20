import config
import datetime, time
import requests, json

class ChannelManager:
    
    def __init__(self, cursor, lock, channelInstances):
        self.cursor = cursor
        self.lock = lock
        self.channelInstances = channelInstances
        
    def run(self):
        # wait for reactor to boot up
        time.sleep(5.0)
        while True:
            print "channel joiner loop"
            # fetch autojoin channels
            autojoins = []
            autojoinRows = []
            enableContests = []
            processJoinParts = True
            try:
                self.lock.acquire(True)
                self.cursor.execute("SELECT channel FROM channels WHERE joinIfLive = ?", (True, ))
                autojoinRows = self.cursor.fetchall()
            finally:
                self.lock.release()
                
            for ajRow in autojoinRows:
                autojoins.append(ajRow["channel"].encode("utf-8"))
                
            
            if config.botNick in autojoins:
                autojoins.remove(config.botNick)
                
            print ",".join(autojoins)
            if len(autojoins) > 0:
                # fetch live channels
                ajURLList = ",".join(autojoins)
                twitchAPIUrl = "https://api.twitch.tv/kraken/streams?channel=%s" % ajURLList
                headers = {'Accept': 'application/vnd.twitchtv.v2+json'}
                liveChannels = []
                r = requests.get(twitchAPIUrl, headers=headers)
                try:
                    jsondata = r.json()
                    for stream in jsondata[u'streams']:
                        liveChannels.append(stream[u'channel'][u'name'].encode("utf-8"))
                        if stream[u'viewers'] >= 10:
                            enableContests.append(stream[u'channel'][u'name'].encode("utf-8"))
                except ValueError:
                    print "request failed"
                    processJoinParts = False
                    
                if processJoinParts:
                    autojoins = [autojoin for autojoin in autojoins if autojoin in liveChannels]
            
            print ",".join(autojoins)            
            # join shit idk
            if processJoinParts:
                from goldenrod import channelInstances
                # join new channels
                for autojoin in autojoins:
                    if autojoin not in channelInstances:
                        from goldenrod import joinNewChannel
                        print "joining %s" % autojoin
                        joinNewChannel(autojoin)
                        
                # leave old channels
                leaveChannels = []
                for channel in channelInstances:
                    if channel != config.botNick and channel not in autojoins:
                        leaveChannels.append(channel)
                    else:
                        channelInstances[channel].contestsEnabled = (channel in enableContests)
                        
                for channel in leaveChannels:
                    from goldenrod import leaveChannel
                    print "leaving %s" % channel
                    leaveChannel(channel, config.byeMessage)
                
            # sleep until next time
            time.sleep(60.0)