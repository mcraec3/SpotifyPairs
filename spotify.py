import json
import re
import requests
from secrets import spotify_user_id,  discover_weekly_id
import time
from refresh import Refresh


class Spotify:
    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = ""
        self.discover_weekly_id = discover_weekly_id
        self.tracks = ""
        self.curr_playlist_id = ""
        #spotify object created, authorize access
        self.acquire_auth()
        self.headr = {"Content-Type": "application/json","Authorization": "Bearer {}".format(self.spotify_token)}

    #sets auth token to curr or new if needed
    def acquire_auth(self):
        print("Checking Auth token")
        with open("C:/Users/cmcra/www/auth.txt") as f:
            lines = f.readlines()
        self.spotify_token=lines[0].strip()

        #check if token is expired
        if (time.time() - int(lines[1]) > 3599):
            #Create Refresh Object
            refreshCaller = Refresh()
            #returns new auth token good for 1 hour
            self.spotify_token = refreshCaller.refresh()
            #write new token values
            with open("C:/Users/cmcra/www/auth.txt", 'w') as f:
                f.write(self.spotify_token + '\n')
                f.write(str(int(time.time())))

    #############################################
    ########## utility functions below ##########
    #############################################

    def get_songs(self, play_id = "id"):

        id_to_use = ""
        
        print("Finding songs in playlist...")
        
        if play_id != "id":
            id_to_use = play_id
        else:
            id_to_use = self.curr_playlist_id
        
        # Loop through playlist tracks, add them to list
        if id_to_use != "":
            query = "https://api.spotify.com/v1/playlists/{}/tracks".format(id_to_use)

            try:
                response = requests.get(query,headers=self.headr).json()
            except json.JSONDecodeError:
                print("Error: No active Spotify session on any devices. Songs not loaded.")

            for i in response["items"]:
                self.tracks += (i["track"]["uri"] + ",")
            self.tracks = self.tracks[:-1]
        else:
            print("ERROR: No valid playlist id given")

    # Create a new playlist and return the playlist id
    def create_playlist(self, title, desc):
    
        print("Trying to create playlist...")

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)

        request_body = json.dumps({ "name": title, "description": desc, "public": True })
        #print(request_body)

        try:
            response = requests.post(query, data=request_body, headers=self.headr).json()
        except json.JSONDecodeError:
            return ""

        return response["id"]

    
    # add all songs in self.tracks to new playlist
    def add_to_playlist(self, play_id = "id"):
        
        id_to_use = ""

        print("Adding songs...")
        if play_id != "id":
            id_to_use = play_id
        else:
            id_to_use = self.curr_playlist_id

        if id_to_use != "":
            query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(self.curr_playlist_id, self.tracks)
            try:
                response = requests.post(query, headers=self.headr).json()
            except json.JSONDecodeError:
                print("ERROR: Could not add tracks to playlist")
        else:
            print("ERROR: No valid current playlist")


    #Acquire info for currently playing track
    def get_current(self): 
        print("Acquiring currently playing")

        info = {}
        artists = ""

        query = "https://api.spotify.com/v1/me/player/currently-playing"
        try:
            response = requests.get(query,headers=self.headr).json()
        except json.JSONDecodeError:
            return info
        
        #Song title and album name
        info['title'] = response['item']['name']
        info['album'] = response['item']['album']['name']

        #Cases for diff num of artists
        num_artists = len(response['item']['artists'])
        if num_artists == 1:
            info['artist'] = response['item']['artists'][0]['name']
        else: 
            for i in range(num_artists - 1):
                artists += response['item']['artists'][i]['name'] + ", "
            artists += "and " + response['item']['artists'][num_artists - 1]['name']
            info['artist'] = artists
        
        #URLs for easy access
        info['song_URL'] = response['item']['external_urls']['spotify']
        info['album_URL'] = response['item']['album']['external_urls']['spotify']
        info['album_art_URL'] = response['item']['album']['images'][1]['url']

        #For when not playing music
        info['seconds_since_played'] = 0
        if not response['is_playing']:
            info['seconds_since_played'] = (int(time.time()-response['timestamp']/1000))
        
        return info

    
    def get_queue(self): 

        query = "https://api.spotify.com/v1/me/player/queue"

        try:
            response = requests.get(query,headers=self.headr).json()
        except json.JSONDecodeError:
            print("ERROR: No valid spotify sessions running")
        
        return(response)
    
    #Puts given URI in queue
    def put_queue(self, push_uri):
        query = "https://api.spotify.com/v1/me/player/queue?uri={}".format(push_uri)
        response = requests.post(query,headers=self.headr)

        return(response)
