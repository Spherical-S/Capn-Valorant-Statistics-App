from json import dump, load
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
mSkinsOutput = {}
lock = Lock()
key = "HDEV-e6ef1170-97c4-4f64-9bc8-dfc4e56b65c5" #not leaking my api key he he he haw (clash royale king laugh)


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


def colorDarken(old_hex):
    r = int(old_hex[1:3], 16)
    g = int(old_hex[3:5], 16)
    b = int(old_hex[5:7], 16)
    r = ceil(r*0.6)
    g = ceil(g*0.6)
    b = ceil(b*0.6)
    if r < 0:
        r = 0
    if g < 0:
        g = 0
    if b < 0:
        b = 0
    r = hex(r)[2:4]
    g = hex(g)[2:4]
    b = hex(b)[2:4]
    if len(r) == 1:
        r = f"0{r}"
    if len(g) == 1:
        g = f"0{g}"
    if len(b) == 1:
        b = f"0{b}"
    return f"#{r}{g}{b}"



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
        'accept': 'application / json',
        'Authorization': key
    }
    url = f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tagline}'
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
    xAct = int(act[1:2]) - 1
    actsDictionary = acts
    puuid = getOtherPUUID(name, tag, region)
    if puuid == "429":
        output = [429, "Error", "N/A", 0, "Error", 0, "Error", "You have been rate limited, try again in ~2 minutes"]
        return output
    elif puuid == "500":
        output = [500, "Error", "N/A", 0, "Error", 0, "Error", "Player does not exist!"]
        return output
    elif puuid == "403":
        output = [403, "Error", "N/A", 0, "Error", 0, "Error", "Couldn't fetch rank! Make sure name is spelled correct!"]
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
    maxRank = MaxRank(region, en, t, puuid)
    if maxRank[0] == -1: #Player has never had a rank
        output = [50, "UNRANKED", "N/A", 0, "UNRANKED", 0, "N/A", "Player has never played ranked, or incorrect region input!"]
        return output
    elif maxRank[0] == 429:
        output = [429, "Error", "N/A", 0, "Error", 0, "Error", "You have been rate limited, try again in ~2 minutes"]
        return output
    else:
        maxrank = x['data'][4]['tiers'][maxRank[0]]['tierName']
        maxSeason = maxRank[1]
        if status != "200":
            output = [-1, "Error", "N/A", 0, "Error", -1, "Error", "Error, please try again later!"]
            return output
        else:
            y = r.json()
            try:
                rankTIER = y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][actsDictionary[act]]["CompetitiveTier"]
                rank = x['data'][xAct]['tiers'][rankTIER]['tierName']
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
def MaxRank(region, en, t, puuid):
    actsDictionary = acts
    oldImmortalPlus = {21: 24, 22: 25, 23: 26, 24: 27}
    ranks = {}
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
    if seasons is None:
        return maxRank
    for i in actsDictionary:
        if actsDictionary[i] in y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
            ranks[actsDictionary[i]] = y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][actsDictionary[i]]
    for i in ranks:
        if ranks[i]["WinsByTier"] is None:
            continue
        for j in ranks[i]["WinsByTier"]:
            tier = int(j)
        if tier >= maxRank[0]:
            maxRank[0] = tier
            maxRank[1] = list(actsDictionary.keys())[list(actsDictionary.values()).index(i)]
            xAct = int(maxRank[1][1:2]) - 1
            if xAct <= 3:
                if maxRank[0] in oldImmortalPlus:
                    maxRank[0] = oldImmortalPlus[maxRank[0]]
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


def getPrices(t, en, region):
    url = f'https://pd.{region}.a.pvp.net/store/v1/offers/'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url, headers=headers)
    y = r.json()
    prices = {}
    for i in range(len(y['Offers'])):
        prices[y['Offers'][i]['Rewards'][0]['ItemID']] = y['Offers'][i]['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
    return prices


# Retrieves the users store
def getStore(t, en, puuid, region):
    getSkins()
    prices = getPrices(t, en, region)
    url = f'https://pd.{region}.a.pvp.net/store/v2/storefront/{puuid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url, headers=headers)
    singleItems = [['', ''], ['', ''], ['', ''], ['', '']]
    if str(r.status_code) == "200":
        y = r.json()
        singleItems[0][0] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][0]]
        singleItems[1][0] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][1]]
        singleItems[2][0] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][2]]
        singleItems[3][0] = weaponsDictionary[y['SkinsPanelLayout']['SingleItemOffers'][3]]
        singleItems[0][1] = prices[y['SkinsPanelLayout']['SingleItemOffers'][0]]
        singleItems[1][1] = prices[y['SkinsPanelLayout']['SingleItemOffers'][1]]
        singleItems[2][1] = prices[y['SkinsPanelLayout']['SingleItemOffers'][2]]
        singleItems[3][1] = prices[y['SkinsPanelLayout']['SingleItemOffers'][3]]
        output = {'status': 200, 'uuids': [y['SkinsPanelLayout']['SingleItemOffers'][0], y['SkinsPanelLayout']['SingleItemOffers'][1], y['SkinsPanelLayout']['SingleItemOffers'][2], y['SkinsPanelLayout']['SingleItemOffers'][3]], 'displayNames': [singleItems[0], singleItems[1], singleItems[2], singleItems[3]], "Message": ""}
        return output
    else:
        output = {'status': -1}
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
    if not y['Players'][i]['PlayerIdentity']['Incognito']:
        nameFromPUUID = getNameFromPUUID(y['Players'][i]['Subject'], region, t)
        name = nameFromPUUID[0]
    else:
        name = "Hidden"
    stats = getPlayerStats(y['Players'][i]['Subject'], region, t, en)
    lock.acquire()
    mStatsOutput[team].append({'puuid': y['Players'][i]['Subject'], 'name': name, 'agent': agentsDictionary[y['Players'][i]['CharacterID']], 'rank': rankData[0], 'rr': rankData[1], 'peak': rankData[2], 'peakSeason': rankData[3], 'stats': stats})
    lock.release()


def playerStatsPre(i, region, en, t, y, team, agentsDictionary):
    global mStatsOutput
    rankData = getMatchRanks(region, en, t, y['AllyTeam']['Players'][i]['Subject'])
    if y['AllyTeam']['Players'][i]['PlayerIdentity']['Incognito']:
        nameFromPUUID = getNameFromPUUID(y['AllyTeam']['Players'][i]['Subject'], region, t)
        name = nameFromPUUID[0]
    else:
        name = "Hidden"
    if y['AllyTeam']['Players'][i]['CharacterID'] != "":
        agent = agentsDictionary[y['AllyTeam']['Players'][i]['CharacterID']]
    else:
        agent = "None"
    stats = getPlayerStats(y['AllyTeam']['Players'][i]['Subject'], region, t, en)
    lock.acquire()
    mStatsOutput[team].append({'puuid': y['AllyTeam']['Players'][i]['Subject'], 'name': name, 'agent': agent, 'rank': rankData[0], 'rr': rankData[1], 'peak': rankData[2], 'peakSeason': rankData[3], 'stats': stats})
    lock.release()


# Gets users match stats
def matchStats(t, en, puuid, region):
    global mStatsOutput
    agentsDictionary = getAgents()
    matchInfo = getCurrentMatchID(t, en, puuid, region)
    matchID = matchInfo[0]
    if matchID != "-1":
        matchid = matchID
    else:
        mStatsOutput = {'status': -1}
        return mStatsOutput
    if matchInfo[1] == "post":
        url = f'https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/matches/{matchid}'
    else:
        url = f'https://glz-{region}-1.{region}.a.pvp.net/pregame/v1/matches/{matchid}'
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url, headers=headers)
    if str(r.status_code) != "200":
        mStatsOutput = {'status': -1}
        return mStatsOutput
    y = r.json()
    if matchInfo[1] == "post":
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
            mStatsOutput['type'] = "post"
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
            mStatsOutput['type'] = "post"
            threads = []
            for i in range(len(players)):
                temp = Thread(target=playerStats, args=(i, region, en, t, y, "players", agentsDictionary,))
                temp.start()
                threads.append(temp)
            for i in range(len(players)):
                threads[i].join()
            return mStatsOutput
    else:
        mStatsOutput = {}
        mStatsOutput['status'] = 200
        mStatsOutput['ffa'] = 0
        mStatsOutput['type'] = "pre"
        mStatsOutput['allies'] = []
        players = y["AllyTeam"]["Players"]
        threads = []
        for i in range(len(players)):
            temp = Thread(target=playerStatsPre, args=(i, region, en, t, y, "allies", agentsDictionary,))
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
    y = r.json()
    if str(r.status_code) != "200":
        url = f'https://glz-{region}-1.{region}.a.pvp.net/pregame/v1/players/{puuid}'
        headers = {
            'X-Riot-Entitlements-JWT': en,
            'Authorization': f'Bearer {t}'
        }
        r = get(url, headers=headers)
        y = r.json()
        if str(r.status_code) != "200":
            return ["-1", "pre"]
        else:
            output = ["", "pre"]
            output[0] = y["MatchID"]
            return output
    else:
        output = ["", "post"]
        output[0] = y["MatchID"]
        return output


# Gets a players max rank for the match stats command
def getMatchRanks(region, en, t, puuid):
    short = {"PLATINUM 1": "PLAT 1", "PLATINUM 2": "PLAT 2", "PLATINUM 3": "PLAT 3",
             "DIAMOND 1": "DIA 1", "DIAMOND 2": "DIA 2", "DIAMOND 3": "DIA 3",
             "ASCENDANT 1": "ASC 1", "ASCENDANT 2": "ASC 2", "ASCENDANT 3": "ASC 3",
             "IMMORTAL 1": "IMM 1", "IMMORTAL 2": "IMM 2", "IMMORTAL 3": "IMM 3"}
    act = getCurrentSeason()
    xAct = int(act[1:2]) - 1
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
    maxRank = MaxRank(region, en, t, puuid)
    if maxRank[0] == -1:
        rank = ["UNRANKED", "N/A", "UNRANKED", "E0A0"]
        return rank
    elif maxRank[0] == 429:
        rank = ["Rate Limit", "N/A", "Rate Limit", "E0A0"]
        return rank
    maxrank = x['data'][xAct]['tiers'][maxRank[0]]['tierName']
    maxSeason = maxRank[1]
    if maxrank in short:
        maxrank = short[maxrank]
    if status != "200":
        return ["Rate Limit", "N/A", "Rate Limit", "E0A0"]
    y = r.json()
    try:
        rankTIER = y["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][actsDictionary[act]]["CompetitiveTier"]
        rank = x['data'][xAct]['tiers'][rankTIER]['tierName']
        if rank in short:
            rank = short[rank]
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


def getWeapons():
    url = "https://valorant-api.com/v1/weapons"
    r = get(url)
    y = r.json()
    weapons = {}
    for i in range(len(y['data'])):
        weapons[y['data'][i]['uuid']] = y['data'][i]['displayName']
    return weapons


def sortSkins(loadout, weapons):
    loadout = loadout['Loadout']['Items']
    skins = {}
    for i in loadout:
        gun = weapons[i]
        skin = weaponsDictionary[loadout[i]['Sockets']['bcef87d6-209b-46c6-8b19-fbe40bd95abc']["Item"]["ID"]]
        skins[gun] = skin
    return skins


def playerSkins(i, region, en, t, players, loadouts, team, agentsDictionary, weapons):
    global mSkinsOutput
    if not players[i]['PlayerIdentity']['Incognito']:
        nameFromPUUID = getNameFromPUUID(players[i]['Subject'], region, t)
        name = nameFromPUUID[0]
    else:
        name = "Hidden"
    agent = agentsDictionary[players[i]['CharacterID']]
    skins = sortSkins(loadouts[i], weapons)
    lock.acquire()
    mSkinsOutput[team].append({'puuid': players[i]['Subject'], 'name': name, 'agent': agent, 'skins': skins})
    lock.release()


def matchSkins(t, en, puuid, region):
    global mSkinsOutput
    getSkins()
    agentsDictionary = getAgents()
    weapons = getWeapons()
    matchInfo = getCurrentMatchID(t, en, puuid, region)
    matchID = matchInfo[0]
    if matchID != "-1":
        matchid = matchID
    else:
        mSkinsOutput = {'status': -1}
        return mSkinsOutput
    if matchInfo[1] != "post":
        return {'status': -2}
    else:
        url = f'https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/matches/{matchid}/loadouts'
        url2 = f"https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/matches/{matchid}"
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}'
    }
    r = get(url2, headers=headers)
    x = r.json()
    r = get(url, headers=headers)
    y = r.json()
    players = x['Players']
    loadouts = y['Loadouts']
    ffa = False
    if x['ModeID'] == '/Game/GameModes/Deathmatch/DeathmatchGameMode.DeathmatchGameMode_C':
        ffa = True
    if ffa == False:
        mSkinsOutput = {}
        mSkinsOutput['status'] = 200
        mSkinsOutput['ffa'] = 0
        mSkinsOutput['blueTeam'] = []
        mSkinsOutput['redTeam'] = []
        mSkinsOutput['type'] = "post"
        threads = []
        for i in range(len(players)):
            if x['Players'][i]['TeamID'] == "Blue":
                temp = Thread(target=playerSkins, args=(i, region, en, t, players, loadouts, "blueTeam", agentsDictionary, weapons,))
                temp.start()
                threads.append(temp)
            else:
                temp = Thread(target=playerSkins, args=(i, region, en, t, players, loadouts, "redTeam", agentsDictionary, weapons,))
                temp.start()
                threads.append(temp)
        for i in range(len(players)):
            threads[i].join()
        return mSkinsOutput
    else:
        mSkinsOutput = {}
        mSkinsOutput['status'] = 200
        mSkinsOutput['ffa'] = 1
        mSkinsOutput['players'] = []
        mSkinsOutput['type'] = "post"
        threads = []
        for i in range(len(players)):
            temp = Thread(target=playerSkins, args=(i, region, en, t, players, loadouts, "players", agentsDictionary, weapons,))
            temp.start()
            threads.append(temp)
        for i in range(len(players)):
            threads[i].join()
        return mSkinsOutput


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


def getPlayerStats(puuid, region, t, en):
    url = f"https://pd.{region}.a.pvp.net/match-history/v1/history/{puuid}/?startIndex=0&endIndex=5&queue=competitive"
    headers = {
        'X-Riot-Entitlements-JWT': en,
        'Authorization': f'Bearer {t}',
        'X-Riot-ClientVersion': getValoVersion(),
        'X-Riot-ClientPlatform': clientPlatform
    }
    r = get(url, headers=headers)
    if r.status_code != 200:
        return {'hs': 'N/A', 'wr': 'N/A', "kd": 'N/A', 'last3': [-1, -1, -1]}
    y = r.json()
    url = f"https://pd.{region}.a.pvp.net/match-history/v1/history/{puuid}/?startIndex=0&endIndex=5&queue=unrated"
    r = get(url, headers=headers)
    if r.status_code != 200:
        return {'hs': 'N/A', 'wr': 'N/A', "kd": 'N/A', 'last3': [-1, -1, -1]}
    x = r.json()
    matchTimes = {}
    matches = []
    for i in range(len(x['History'])):
        matchTimes[int(x['History'][i]['GameStartTime'])] = x['History'][i]['MatchID']
    for i in range(len(y['History'])):
        matchTimes[int(y['History'][i]['GameStartTime'])] = y['History'][i]['MatchID']
    if len(matchTimes.keys()) < 5:
        return {'hs': 'N/A', 'wr': 'N/A', "kd": 'N/A', 'last3': [-1, -1, -1]}
    for i in sorted(matchTimes.keys(), reverse=True):
        matches.append(matchTimes[i])
        if len(matches) == 5:
            break
    matchDatas = []
    for i in range(5):
        url = f"https://pd.{region}.a.pvp.net/match-details/v1/matches/{matches[i]}"
        r = get(url, headers=headers)
        if r.status_code != 200:
            return {'hs': 'N/A', 'wr': 'N/A', "kd": 'N/A', 'last3': [-1, -1, -1]}
        matchDatas.append(r.json())
    count = 0
    last3 = [-1, -1, -1]
    wins = 0
    losses = 0
    kills = 0
    deaths = 0
    headshots = 0
    othershots = 0
    for i in matchDatas:
        team = ""
        for j in i['players']:
            if j['subject'] == puuid:
                team = j['teamId']
        for j in i['teams']:
            if j["teamId"] == team:
                if j["won"] == True:
                    if count < 3:
                        last3[count] = 1
                    wins += 1
                else:
                    if count < 3:
                        last3[count] = 0
                    losses += 1
        for j in i['roundResults']:
            for k in j['playerStats']:
                if k['subject'] == puuid:
                    for l in k['damage']:
                        headshots += int(l['headshots'])
                        othershots += int(l['legshots'])
                        othershots += int(l['bodyshots'])
        for j in i['kills']:
            if j['victim'] == puuid:
                deaths += 1
            if j['killer'] == puuid:
                kills += 1
        count += 1
    wr = round((wins/(wins+losses))*100)
    kd = round(kills/deaths, 2)
    hs = round((headshots/othershots)*100)
    return {'hs': f'{hs}%', 'wr': f'{wr}%', "kd": f'{kd}', 'last3': last3}
