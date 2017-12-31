from json import load, dump
from requests import post, get
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from webbrowser import open as webopen
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import exit
from datetime import datetime
from yaml import dump as ydump



with open('client_secret.json') as f:
    cs = load(f)['installed']



def show_auth_page():
    u = list(urlparse(cs['auth_uri']))
    u[4] = urlencode({
        'client_id': cs['client_id'],
        'redirect_uri': 'http://localhost:10000',
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/youtube.readonly'
    })
    webopen(urlunparse(u))

def listen_for_code():
    finished = False
    re = None
    class S(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal finished, re
            url = urlparse(self.path)
            if url.path == '/':
                re = parse_qs(url.query)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("<html><head><title>OAuth</title></head><body><h1>Now you can close this window/tab.</h1></body></html>".encode('utf-8'))
                finished = True
            else:
                self.send_response(204)
                self.end_headers()
    httpd = HTTPServer(('localhost', 10000), S)
    while not finished:
        httpd.handle_request()
    return {k: ', '.join(v) for k, v in re.items()}

def request_token(code):
    r = post(cs['token_uri'], data={
        'code': code,
        'client_id': cs['client_id'],
        'client_secret': cs['client_secret'],
        'redirect_uri': 'http://localhost:10000',
        'grant_type': 'authorization_code'
    })
    d = int(datetime.strptime(r.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z').timestamp())
    r = r.json()
    r.pop('token_type')
    e = r.pop('expires_in')
    r['expires_at'] = d + e
    return r

def refresh_token(refresh_token):
    r = post(cs['token_uri'], data={
        'refresh_token': refresh_token,
        'client_id': cs['client_id'],
        'client_secret': cs['client_secret'],
        'grant_type': 'refresh_token'
    })
    d = int(datetime.strptime(r.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z').timestamp())
    r = r.json()
    r.pop('token_type')
    e = r.pop('expires_in')
    r['expires_at'] = d + e
    return r



def auth():
    show_auth_page()
    code = listen_for_code()
    if 'error' in code:
        print('An error occured during the authentication process:')
        print(code['error'])
        exit(1)

    cred = request_token(code['code'])

    with open('credentials.json', 'w') as f:
        dump(cred, f)

def refresh():
    new_cred = refresh_token(cred['refresh_token'])
    cred.update(new_cred)
    with open('credentials.json', 'w') as f:
        dump(cred, f)



def apireq(path, params={}):
    _params = {'part': 'snippet'}
    _params.update(params)
    baseURL = 'https://www.googleapis.com/youtube/v3'
    r = get(baseURL + path, params=_params, headers={'Authorization': 'Bearer %s' % cred['access_token']})
    if r.status_code == 401:
        refresh()
        return apireq(path, params)
    return r.json()

def apireqlist(path, params={}):
    _params = {'maxResults': 50}
    _params.update(params)
    r = apireq(path, _params)
    re = r['items']
    if 'nextPageToken' in r:
        _params['pageToken'] = r['nextPageToken']
        re += apireqlist(path, _params)
    return re



try:
    with open('credentials.json') as f:
        cred = load(f)
except FileNotFoundError as e:
    auth()



playlists = apireqlist('/playlists', {'mine': 'true'})
out = [{'id': x['id'], 'title': x['snippet']['title']} for x in playlists]
out = sorted(out, key=lambda x: x['title'])

for pl in out:
    print('Downloading [%s] ' % pl['title'], end='')
    items = apireqlist('/playlistItems', {'playlistId': pl['id']})
    pl['items'] = [{'id': x['snippet']['resourceId']['videoId'], 'title': x['snippet']['title']} for x in items]
    print(' Done')

with open('dump.yaml', 'w') as f:
    ydump(out, f, width=250)
