from tkinter import messagebox
from requests import get, put
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageTk
from math import ceil
from http.client import HTTPSConnection
from string import ascii_lowercase
from random import choice
from threading import Thread, Lock

clientPlatform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
acts = {}
agents = {}
weaponsDictionary = {}
mStatsOutput = []
lock = Lock()


def internet():
    conn = HTTPSConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        messagebox.showerror("Connection Error", "Please check your internet connection then try again!")
        quit()
    finally:
        conn.close()


def randomString(length):
    # choose from all lowercase letter
    letters = ascii_lowercase
    result_str = ''.join(choice(letters) for i in range(length))
    return result_str


# Turns a url image into a valid photo image to be displayed in tkinter
def photoImagify(url):
    img_data = get(url).content
    img_open = Image.open(BytesIO(img_data))
    img = ImageTk.PhotoImage(img_open)
    while img.height() > 200:
        img_resize = img_open.resize((ceil(img.width()*0.99), ceil(img.height()*0.99)))
        img = ImageTk.PhotoImage(img_resize)
    while img.width() > 550:
        img_resize = img_open.resize((ceil(img.width() * 0.99), ceil(img.height() * 0.99)))
        img = ImageTk.PhotoImage(img_resize)
    return img


# getActs() retrieves all previous and current acts so that i don't have to manually update the acts dictionary
def getActs():
    global acts
    url = 'https://valorant-api.com/v1/seasons'
    r = get(url)
    y = r.json()
    episode = 0
    acts = {}
    for i in range(len(y['data'])):
        if (i - 1) % 4 == 0:
            episode += 1
        elif i == 0:
            continue
        elif (i - 1) % 4 == 1:
            acts['E' + str(episode) + 'A1'] = y['data'][i]['uuid']
        elif (i - 1) % 4 == 2:
            acts['E' + str(episode) + 'A2'] = y['data'][i]['uuid']
        elif (i - 1) % 4 == 3:
            acts['E' + str(episode) + 'A3'] = y['data'][i]['uuid']
    return acts


# getAgents() retreives all the agents and their ids in game
def getAgents():
    global agents
    url = 'https://valorant-api.com/v1/agents'
    r = get(url)
    y = r.json()
    for i in range(len(y['data'])):
        agents[y['data'][i]['uuid']] = y['data'][i]['displayName']
        agents[y['data'][i]['uuid'].upper()] = y['data'][i]['displayName']
    return agents


# indexOf() returns the index of a string within a string, returns -1 if string not found
def indexOf(s, find):
    for i in range(len(s)):
        if s[i:i+len(find)] == find:
            return i
    return -1


def getCurrentSeason():
    url = 'https://valorant-api.com/v1/seasons'
    r = get(url)
    y = r.json()
    episode = 0
    count = 0
    currentDate = int(datetime.today().strftime('%Y%m%d'))
    for i in y['data']:
        if (count - 1) % 4 == 0:
            episode += 1
        else:
            seStart = i['startTime'][0:indexOf(i['startTime'], 'T')]
            seEnd = i['endTime'][0:indexOf(i['endTime'], 'T')]
            seStart = seStart[0:4] + seStart[5:7] + seStart[8:10]
            seEnd = seEnd[0:4] + seEnd[5:7] + seEnd[8:10]
            if currentDate >= int(seStart) and currentDate <= int(seEnd):
                if (count - 1) % 4 == 1:
                    return f'E{episode}A1'
                if (count - 1) % 4 == 2:
                    return f'E{episode}A2'
                if (count - 1) % 4 == 3:
                    return f'E{episode}A3'
        count += 1


# returns the current valorant version
def getValoVersion():
    url = 'https://valorant-api.com/v1/version'
    r = get(url)
    y = r.json()
    return y['data']['riotClientVersion']


# gets a player puuid with their name and tag
def getOtherPUUID(name, tagline, region):
    headers = {
        'accept': 'application / json'
    }
    url = f'https://api.henrikdev.xyz/valorant/v2/mmr/{region.lower()}/{name}/{tagline}'
    r = get(url, headers=headers)
    y = r.json()
    if r.status_code == 200:
        puuid = y['data']['puuid']
        return puuid
    elif r.status_code == 429:
        return "429"
    elif r.status_code == 500:
        return "500"
    else:
        return "403"


# gets a players current and peak rank using their name tag and region
def getRankByName(name, tag, region, act, t, en):
    # STATUS CODES:
    # 429: rate limit
    # 500: user doesnt exist
    # 50: player has never had a rank
    # -1: unknown error
    # 150: unranked but has had a max rank
    # 200: all data present
    # 100: player has not played ranked in the given act
    actsDictionary = acts
    puuid = getOtherPUUID(name, tag, region)
    if puuid == "429":
        output = [429, "Error", "N/A", 0, "Error", 0, "Error", "You have been rate limited, try again in ~2 minutes"]
        return output
    elif puuid == "500":
        output = [500, "Error", "N/A", 0, "Error", 0, "Error", "Player does not exist!"]
        return output
    elif puuid == "403":
        output = [403, "Error", "N/A", 0, "Error", 0, "Error", "Couldn't fetch rank! Try contacting dev in help section!"]
        return output
    url = f'https://pd.{region}.a.pvp.net/mmr/v1/players/{puuid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}',
        'X-Riot-ClientVersion': getValoVersion(),
        'X-Riot-ClientPlatform': clientPlatform
    }
    r = get(url, headers=headers)
    status = str(r.status_code)
    r2 = get('https://valorant-api.com/v1/competitivetiers')
    x = r2.json()
    maxRank = getMaxRank(region, en, t, puuid)
    if maxRank[0] == -1: #Player has never had a rank
        output = [50, "UNRANKED", "N/A", 0, "UNRANKED", 0, "N/A", "Player has never played ranked, or incorrect region input!"]
        return output
    elif maxRank[0] == 429:
        output = [429, "Error", "N/A", 0, "Error", 0, "Error", "You have been rate limited, try again in ~2 minutes"]
        return output
    else:
        maxrank = x['data'][0]['tiers'][maxRank[0]]['tierName']
        maxSeason = maxRank[1]
        if status != "200":
            output = [-1, "Error", "N/A", 0, "Error", -1, "Error", "Error, please try again later!"]
            return output
        else:
            y = r.json()
            try:
                rankTIER = y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][actsDictionary[act]]["CompetitiveTier"]
                rank = x['data'][0]['tiers'][rankTIER]['tierName']
                if rank == 'UNRANKED':
                    output = [150, "UNRANKED", "N/A", rankTIER, maxrank, maxRank[0], maxSeason, ""]
                    return output
                else:
                    mmr = y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][actsDictionary[act]]["RankedRating"]
                    mmr = str(mmr)
                    if rankTIER < 21:
                        if len(mmr) > 2:
                            mmr = mmr[1:]
                        if len(mmr) > 3:
                            mmr = mmr[2:]
                    output = [200, rank, mmr, rankTIER, maxrank, maxRank[0], maxSeason, ""]
                    return output
            except KeyError:
                output = [100, "UNRANKED", "N/A", 0, maxrank, maxRank[0], maxSeason, "Player did not play ranked in the given act!"]
                return output


# Gets a players max rank and max season using their puuid
def getMaxRank(region, en, t, puuid):
    actsDictionary = acts
    url = f'https://pd.{region}.a.pvp.net/mmr/v1/players/{puuid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}',
        'X-Riot-ClientVersion': getValoVersion(),
        'X-Riot-ClientPlatform': clientPlatform
    }
    r = get(url, json={}, headers=headers)
    if str(r.status_code) != "200":
        return [-1]
    if str(r.status_code) == "429":
        return [429]
    y = r.json()
    maxRank = [-1, '']
    seasons = y["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")
    if seasons is not None:
        for season in y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
            if y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"] is not None:
                for winByTier in y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"]:
                    if int(winByTier) > maxRank[0]:
                        maxRank[1] = list(actsDictionary.keys())[list(actsDictionary.values()).index(season)]
                        maxRank[0] = int(winByTier)
    return maxRank


def getSkins():
    global weaponsDictionary
    url = 'https://valorant-api.com/v1/weapons'
    r = get(url)
    y = r.json()
    for i in range(len(y['data'])):
        weaponsDictionary[y['data'][i]['uuid']] = y['data'][i]['displayName']
        for n in range(len(y['data'][i]['skins'])):
            weaponsDictionary[y['data'][i]['skins'][n]['uuid']] = y['data'][i]['skins'][n]['displayName']
            for j in range(len(y['data'][i]['skins'][n]['chromas'])):
                weaponsDictionary[y['data'][i]['skins'][n]['chromas'][j]['uuid']] = y['data'][i]['skins'][n]['displayName']
                for l in range(len(y['data'][i]['skins'][n]['levels'])):
                    weaponsDictionary[y['data'][i]['skins'][n]['levels'][l]['uuid']] = y['data'][i]['skins'][n]['displayName']


# Retrieves the users store
def getStore(t, en, puuid, region):
    getSkins()
    url = f'https://pd.{region}.a.pvp.net/store/v2/storefront/{puuid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url, headers=headers)
    singleItems = ['', '', '', '']
    if str(r.status_code) == "200":
        y = r.json()
        singleItems[0] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][0]]
        singleItems[1] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][1]]
        singleItems[2] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][2]]
        singleItems[3] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][3]]
        output = {'uuids': [y['SkinsPanelLayout']['SingleItemOffers'][0], y['SkinsPanelLayout']['SingleItemOffers'][1], y['SkinsPanelLayout']['SingleItemOffers'][2], y['SkinsPanelLayout']['SingleItemOffers'][3]], 'displayNames': [singleItems[0], singleItems[1], singleItems[2], singleItems[3]], "Message": ""}
        return output
    else:
        output = {'uuids': ["-1", "-1", "-1", "-1"], "displayNames": ["Error", "Error", "Error", "Error"], "Message": "Couldn't retrieve store, try again later."}
        return output


# Gets users balance
def getBalance(t, en, puuid, region):
    url = f'https://pd.{region}.a.pvp.net/store/v1/wallet/{puuid}'
    headers = headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url, headers=headers)
    balance = [0, 0]
    if str(r.status_code) == "200":
        y = r.json()
        balance[0] = y['Balances']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
        balance[1] = y['Balances']['e59aa87c-4cbf-517a-5983-6e81511be9b7']
        return balance
    else:
        return ["Error", "Error"]


def playerStats(i, region, en, t, y, team, agentsDictionary):
    global mStatsOutput
    rankData = getMatchRanks(region, en, t, y['Players'][i]['Subject'])
    nameFromPUUID = getNameFromPUUID(y['Players'][i]['Subject'], region, t)
    name = nameFromPUUID[0]
    lock.acquire()
    mStatsOutput[team].append({'puuid': y['Players'][i]['Subject'], 'name': name, 'agent': agentsDictionary[y['Players'][i]['CharacterID']], 'rank': rankData[0], 'rr': rankData[1], 'peak': rankData[2], 'peakSeason': rankData[3]})
    lock.release()


# Gets users match stats
def matchStats(t, en, puuid, region):
    global mStatsOutput
    agentsDictionary = getAgents()
    matchID = getCurrentMatchID(t, en, puuid, region)
    if matchID != "-1":
        matchid = matchID
    else:
        mStatsOutput = {'status': -1}
        return mStatsOutput
    url = f'https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/matches/{matchid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url, headers=headers)
    if str(r.status_code) != "200":
        mStatsOutput = {'status': -1}
        return mStatsOutput
    y = r.json()
    players = y['Players']
    ffa = False
    if y['ModeID'] == '/Game/GameModes/Deathmatch/DeathmatchGameMode.DeathmatchGameMode_C':
        ffa = True
    if ffa == False:
        mStatsOutput = {}
        mStatsOutput['status'] = 200
        mStatsOutput['ffa'] = 0
        mStatsOutput['blueTeam'] = []
        mStatsOutput['redTeam'] = []
        threads = []
        for i in range(len(players)):
            if y['Players'][i]['TeamID'] == "Blue":
                temp = Thread(target=playerStats, args=(i, region, en, t, y, "blueTeam", agentsDictionary,))
                temp.start()
                threads.append(temp)
            else:
                temp = Thread(target=playerStats, args=(i, region, en, t, y, "redTeam", agentsDictionary,))
                temp.start()
                threads.append(temp)
        for i in range(len(players)):
            threads[i].join()
        return mStatsOutput
    else:
        mStatsOutput = {}
        mStatsOutput['status'] = 200
        mStatsOutput['ffa'] = 1
        mStatsOutput['players'] = []
        threads = []
        for i in range(len(players)):
            temp = Thread(target=playerStats, args=(i, region, en, t, y, "players", agentsDictionary,))
            temp.start()
            threads.append(temp)
        for i in range(len(players)):
            threads[i].join()
        return mStatsOutput



# gets the players match ID
def getCurrentMatchID(t, en, puuid, region):
    url = f'https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/players/{puuid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url, headers=headers)
    y = r.text
    if str(r.status_code) != "200":
        return "-1"
    else:
        output = y[indexOf(y, 'MatchID') + 10:indexOf(y, '","Version')]
        return output


# Gets a players max rank for the match stats command
def getMatchRanks(region, en, t, puuid):
    act = getCurrentSeason()
    actsDictionary = acts
    url = f'https://pd.{region}.a.pvp.net/mmr/v1/players/{puuid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}',
        'X-Riot-ClientVersion': getValoVersion(),
        'X-Riot-ClientPlatform': clientPlatform
    }
    r = get(url, headers=headers)
    status = str(r.status_code)
    r2 = get('https://valorant-api.com/v1/competitivetiers')
    x = r2.json()
    maxRank = getMaxRank(region, en, t, puuid)
    if maxRank[0] == -1:
        rank = ["UNRANKED", "N/A", "UNRANKED", "E0A0"]
        return rank
    elif maxRank[0] == 429:
        rank = ["Rate Limit", "N/A", "Rate Limit", "E0A0"]
    maxrank = x['data'][0]['tiers'][maxRank[0]]['tierName']
    maxSeason = maxRank[1]
    if status != "200":
        return ["Rate Limit", "N/A", "Rate Limit", "E0A0"]
    y = r.json()
    try:
        rankTIER = y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][actsDictionary[act]]["CompetitiveTier"]
        rank = x['data'][0]['tiers'][rankTIER]['tierName']
        if rank == 'UNRANKED':
            output = ['UNRANKED', 'N/A', maxrank, maxSeason]
            return output
        else:
            mmr = y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][actsDictionary[act]]["RankedRating"]
            mmr = str(mmr)
            if rankTIER < 21:
                if len(mmr) > 2:
                    mmr = mmr[1:]
                if len(mmr) > 3:
                    mmr = mmr[2:]
            output = [rank, mmr, maxrank, maxSeason]
            return output
    except KeyError:
        output = ['UNRANKED', 'N/A', maxrank, maxSeason]
        return output


# Gets a players name from their puuid
def getNameFromPUUID(puuid, region, token):
    output = ['', '']
    url = f"https://pd.{region}.a.pvp.net/name-service/v2/players"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = put(url, headers=headers, json=[puuid], verify=False)
    status = str(response.status_code)
    if status != "200":
        output = ["Rate Limited", "Err"]
    output[0] = response.json()[0]["GameName"]
    output[1] = response.json()[0]["TagLine"]
    return output