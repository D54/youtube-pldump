import logging

import json
import webbrowser

import codecs

import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage

logging.basicConfig()

storage = Storage('credentials.json')
credentials = storage.get()

if credentials is None:
    flow = client.flow_from_clientsecrets(
    'client_secret.json',
    scope='https://www.googleapis.com/auth/youtube.readonly',
    redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    auth_uri = flow.step1_get_authorize_url()
    webbrowser.open(auth_uri)

    auth_code = raw_input('Enter the auth code: ')

    credentials = flow.step2_exchange(auth_code)

    storage.put(credentials)


http_auth = credentials.authorize(httplib2.Http())

youtube = discovery.build('youtube', 'v3', http=http_auth)

request = youtube.playlists().list(part="snippet", mine=True)

playlists = []

while request is not None:
    response = request.execute()

    for pl in response['items']:
        playlists.append({'title': pl['snippet']['title'], 'id': pl['id']})

    request = youtube.playlists().list_next(request, response)


f = codecs.open('dump.txt','w', 'utf-8')

for pl in playlists:
    print pl['title']
    f.write("%s\n" % pl['title'])

    request = youtube.playlistItems().list(part='snippet',playlistId=pl['id'])

    while request is not None:
        response = request.execute()

        for pli in response['items']:
            f.write("   %s   %3d  %s\n" % (pli['snippet']['resourceId']['videoId'], pli['snippet']['position'], pli['snippet']['title']))

        request = youtube.playlistItems().list_next(request, response)

    f.write("\n")

f.close()
