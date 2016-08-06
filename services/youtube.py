import httplib2
import os
import sys
import requests

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from services.service import Service
from servicetrack import ServiceTrack

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

client_secrets_file = 'youtube_client_secret.json'

class Youtube(Service):
    name = "YouTube"
    
    def __init__(self, config):
        self.youtube = self.get_authenticated_service(client_secrets_file)
        self.config = config
    
    def get_authenticated_service(self, client_secrets_file):
        '''
        Return an authenticated youtube api client.
        
        @param client_secrets_file The file path of a client secrets json file
        '''
        flow = flow_from_clientsecrets(client_secrets_file,
            scope=YOUTUBE_READ_WRITE_SCOPE,
            message=MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)

        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()))
            # developerKey=config['api_key']
    
    def search_first(self, query):
        '''
        Search youtube for `query` and return the id and title of the first result
        Returns None on no video found.
        video_id = result['id']['videoId']
        video_title = result['snippet']['title']
        '''
        search_response = self.youtube.search().list(
            q=query,
            part="snippet",
            maxResults=1,
            type="video"
        ).execute()
        
        if search_response['pageInfo']['totalResults'] < 1:
            return None
        
        return search_response['items'][0]
        
    def search(self, track):
        '''
        @param track A pylast track object
        @return A list containing up to one ServiceTrack
        '''
        q = track.artist.name + ' ' + track.title
        result = self.search_first(q)
        if not result:  # No video found
            return []
        video_id = result['id']['videoId']
        video_title = result['snippet']['title']
        st = ServiceTrack('Insert "{}" into playlist'.format(video_title))
        st.id = video_id
        return [st]
        
    def save(self, servicetrack):
        '''
        Adds the track to the user's playlist
        
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        playlists_insert_response = self.youtube.playlistItems().insert(
            part="snippet",
            body = {
                "snippet": {
                    "playlistId": self.config['playlist_id'],
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": servicetrack.id
                    }
                }
            }
        ).execute()
        # Assume success; an HttpError would have been raised on failure.
        # That exception will be handled by the main module.
        return (True, 'Saved to YouTube playlist')