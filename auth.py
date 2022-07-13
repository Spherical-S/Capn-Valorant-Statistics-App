from requests import session as sesh
from requests.adapters import HTTPAdapter
from ssl import PROTOCOL_TLSv1_2
from urllib3 import PoolManager
from tkinter import *
from collections import OrderedDict
from re import compile
from json import load
from time import sleep
from os import startfile
from cryptocode import decrypt, encrypt
from datetime import datetime
from configparser import ConfigParser


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_version=PROTOCOL_TLSv1_2)

def checkLogins(): #Checks if user is logged in, if they are check if the logins are valid or ask for 2fa code
    settings = ConfigParser()
    settings.read("settings.ini")
    enc_key = settings['DEFAULT']['CAPNKEY']
    output = [0] #[0] means success, [1] means fail
    if settings['DEFAULT']['username'] == "" or settings['DEFAULT']['password'] == "" or settings['DEFAULT']['region'] == "":
        output = [1, "", "", "", ""]
        return output #1 means not logged in or incorrect details
    else:
        if settings['DEFAULT']['mfa'] == "1":
            now = datetime.now()
            time = int(now.strftime("%Y%m%d%H%M%S"))
            expiry = int(settings['DEFAULT']['expiry'])
            if expiry >= time:
                return [0]
            else:
                output = [1]
                return output
        else:
            authorize = getAuth(decrypt(settings['DEFAULT']['username'], enc_key), decrypt(settings['DEFAULT']['password'], enc_key))
            if authorize[0] == "-1":
                output = [1]
                return output
            else:
                output = [0]
                return output


def getAuth(username, password):
    settings = ConfigParser()
    settings.read("settings.ini")
    enc_key = settings['DEFAULT']['CAPNKEY']
    headers = OrderedDict({
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*",
        'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)'
    })
    session = sesh()
    session.headers = headers
    session.mount('https://', TLSAdapter())
    data = {
        "client_id": "play-valorant-web-prod",
        "nonce": "1",
        "redirect_uri": "https://playvalorant.com/opt_in",
        "response_type": "token id_token",
        'scope': 'account openid',
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)',
    }
    r = session.post(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    r = session.put(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    data = r.json()
    mfa = "0"
    if data['type'] == 'auth':
        session.close()
        return ["-1"]
    elif data['type'] == 'multifactor':
        mfa = "1"
        start = settings['DEFAULT']['check']
        startfile("multifactorauth.exe")
        while True:
            settings.read('settings.ini')
            if settings['DEFAULT']['check'] != start:
                break
            sleep(1)
        data = {
            "type": "multifactor",
            "code": settings['DEFAULT']['code'],
            "rememberDevice": "True"
        }
        r2 = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
        data = r2.json()

    pattern = compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    data = pattern.findall(data['response']['parameters']['uri'])[0]
    token = data[0]

    headers = {
        'User-Agent': 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)',
        'Authorization': f'Bearer {token}',
    }
    r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
    entitlement = r.json()['entitlements_token']

    r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
    data = r.json()
    puuid = data['sub']
    settings['DEFAULT']['username'] = encrypt(username, enc_key)
    settings['DEFAULT']['password'] = encrypt(password, enc_key)
    settings['DEFAULT']['token'] = encrypt(token, enc_key)
    settings['DEFAULT']['entitlement'] = encrypt(entitlement, enc_key)
    settings['DEFAULT']['puuid'] = puuid
    settings['DEFAULT']['mfa'] = mfa
    f = open('settings.ini', 'w')
    settings.write(f)
    f.close()
    return ["0"]