import config
import datetime, time
import requests, json

class ChannelManager:
    
    def __init__(self, conn, cursor, lock, channelInstances):
        self.conn = conn
        self.cursor = cursor
        self.lock = lock
        self.channelInstances = channelInstances
        
    def run(self):
        # wait for reactor to boot up
        time.sleep(5.0)
        lastOnlineList = []
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
                broadcastIDs = {}
                r = requests.get(twitchAPIUrl, headers=headers)
                try:
                    jsondata = r.json()
                    for stream in jsondata[u'streams']:
                        liveChannels.append(stream[u'channel'][u'name'].encode("utf-8"))
                        broadcastIDs[stream[u"_id"]] = stream[u'channel'][u'name'].encode("utf-8")
                        if stream[u'viewers'] >= 10:
                            enableContests.append(stream[u'channel'][u'name'].encode("utf-8"))
                except ValueError:
                    print "request failed"
                    processJoinParts = False
                    
                if processJoinParts:
                    autojoins = [autojoin for autojoin in autojoins if autojoin in liveChannels]
                    preparedINs = ["?"] * len(broadcastIDs)
                    inString = ",".join(preparedINs)
                    preparedIDs = [id for id in broadcastIDs]
                    try:
                        self.lock.acquire(True)
                        self.cursor.execute("SELECT * FROM broadcast_history WHERE id IN(%s)" % inString, preparedIDs)
                        bhRows = self.cursor.fetchall()
                        updateIDs = []
                        for row in bhRows:
                            del broadcastIDs[row["id"]]
                            self.cursor.execute("UPDATE broadcast_history SET last_seen = ? WHERE id = ?", (datetime.datetime.now(), row["id"]))
                        
                        for newID in broadcastIDs:
                            self.cursor.execute("INSERT INTO broadcast_history (id, channel, first_seen, last_seen) VALUES(?, ?, ?, ?)", (newID, broadcastIDs[newID], datetime.datetime.now(), datetime.datetime.now()))
                        
                        self.conn.commit()
                    finally:
                        self.lock.release()
            
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
                    if channel != config.botNick and channel not in autojoins and channel not in lastOnlineList:
                        leaveChannels.append(channel)
                    else:
                        channelInstances[channel].contestsEnabled = (channel in enableContests)
                        
                for channel in leaveChannels:
                    from goldenrod import leaveChannel
                    print "leaving %s" % channel
                    leaveChannel(channel, config.byeMessage)
            
            # cycle through last online
            lastOnlineList = autojoins
            
            # sleep until next time
            time.sleep(60.0)