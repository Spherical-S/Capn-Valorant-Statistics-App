from requests import session as sesh
from requests.adapters import HTTPAdapter
import ssl
from tkinter import *
from collections import OrderedDict
from typing import Any
from re import compile
from json import load
from time import sleep
from os import environ, startfile
from cryptocode import decrypt
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def checkLogins(): #Checks if user is logged in, if they are check if the logins are valid or ask for 2fa code
    global logins
    output = [0, "", "", "", ""] #[0] holds value for if login was success, [1] holds token, [2] holds entitlement, [3] holds puuid, [4] holds value for mfa
    f = open('config.json', 'r')
    logins = load(f)
    f.close()
    if logins['username'] == "" and logins['password'] == "" and logins['region'] == "":
        output = [1, "", "", "", ""]
        return output #1 means not logged in or incorrect details
    else:
        if logins['mfa'] == "1":
            now = datetime.now()
            time = int(now.strftime("%Y%m%d%H%M%S"))
            expiry = int(logins['expiry'])
            if expiry >= time:
                return [0, decrypt(logins['token'], environ.get('CAPNKEY')), decrypt(logins['entitlement'], environ.get('CAPNKEY')), logins['puuid'], '1']
            else:
                output = [1, "", "", "", ""]
                return output
        else:
            authorize = getAuth(decrypt(logins['username'], environ.get('CAPNKEY')), decrypt(logins['password'], environ.get('CAPNKEY')))
            if authorize[0] == "-1":
                output = [1, "", "", ""]
                return output
            else:
                token = authorize[0]
                en = authorize[1]
                puuid = authorize[2]
                output = [0, token, en, puuid, "0"]
                return output


def getAuth(username, password):
    headers = OrderedDict({
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*"
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
        return ["-1", "0"]
    elif data['type'] == 'multifactor':
        mfa = "1"
        f = open('multifactor.json', 'r')
        start = load(f)
        f.close()
        startfile("multifactorauth.exe")
        while True:
            f = open('multifactor.json', 'r')
            temp = load(f)
            f.close()
            if temp['check'] != start['check']:
                break
            sleep(1)
        data = {
            "type": "multifactor",
            "code": temp['code'],
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
    
    return [token, entitlement, puuid, mfa]