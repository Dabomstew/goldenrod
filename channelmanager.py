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
        lastChannelList = []
        while True:
            try:
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
                    
                if len(autojoins) > 0:
                    # fetch live channels
                    ajURLList = ",".join(autojoins)
                    twitchAPIUrl = "https://api.twitch.tv/kraken/streams?channel=%s" % ajURLList
                    headers = {'Accept': 'application/vnd.twitchtv.v2+json', 'Client-ID': config.botClientID}
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
                                self.cursor.execute("UPDATE broadcast_history SET last_seen = ? WHERE id = ?", (int(time.time()), row["id"]))
                            
                            for newID in broadcastIDs:
                                self.cursor.execute("INSERT INTO broadcast_history (id, channel, first_seen, last_seen) VALUES(?, ?, ?, ?)", (newID, broadcastIDs[newID], int(time.time()), int(time.time())))
                            
                            self.conn.commit()
                        finally:
                            self.lock.release()
                         
                # join shit idk
                if processJoinParts:
                    from goldenrod import channelInstances
                    # join new channels
                    for autojoin in autojoins:
                        if autojoin not in channelInstances:
                            from goldenrod import joinNewChannel
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
                        leaveChannel(channel, config.byeMessage)
                
                # cycle through last online
                lastOnlineList = autojoins
                
                # check for stray instances
                from goldenrod import channelInstances, allInstances
                channelList = []
                for channel in channelInstances:
                    channelList.append(channelInstances[channel])
                    
                for instance in allInstances:
                    if instance not in channelList and instance not in lastChannelList:
                        # silently kill this instance
                        instance.leaveChannel("")
                        
                # cycle through instance list
                lastChannelList = channelList
            except SysCallError:
                pass
            except SSLError:
                pass
            except KeyError:
                pass
            # sleep until next time
            time.sleep(60.0)