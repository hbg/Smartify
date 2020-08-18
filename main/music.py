import requests
import urllib.parse
import os
import math, random, json

API_KEY = os.environ.get("API_KEY")
REQUEST_PROPERTIES = {}


def set_properties(api_key):
    if api_key == None:
        return
    global REQUEST_PROPERTIES
    REQUEST_PROPERTIES = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }


set_properties(API_KEY)


class Track:

    def __init__(self, id):
        self.id = id

    def get_properties(self):
        req = requests.get(
            "https://api.spotify.com/v1/audio-features/" + self.id,
            headers=REQUEST_PROPERTIES)
        self.properties = req.json()
        return self.properties


class Album:
    REQUEST_URL_ALBUM = "https://api.spotify.com/v1/albums/"
    REQUEST_URL_PLAYLIST = "https://api.spotify.com/v1/playlists/"

    def __init__(self, ID, album):
        self.id = ID
        self.regenerate_token()
        self.played = []
        self.current_song = {}
        self.current_song_properties = {}
        self.scores = []
        self.is_album = album
        self.play_index = 0
        self.std_dev = 0.0

    @staticmethod
    def find(name, is_album=False):
        # Repeated code here b/c staticmethod
        global REQUEST_PROPERTIES
        req = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization":
                    "Basic " + os.environ.get("BASE64_ENCODED")
            },
            data={
                "grant_type": "client_credentials"
            }
        )
        REQUEST_PROPERTIES = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + req.json()["access_token"],
        }
        if is_album:
            URL = "https://api.spotify.com/v1/search?q=album%3A" + name + "&type=album"
        else:
            URL = "https://api.spotify.com/v1/search?q=" + name + "&type=playlist"
        req = requests.get(URL,
                           headers=REQUEST_PROPERTIES)
        results = req.json()["albums"
        if is_album else "playlists"]["items"]
        return results

    def move_back(self):
        ""
        # Removes current song from played
        self.played.pop()
        # Current song is two indices back
        new_song = self.played[-1]
        self.play(new_song)
        self.play_index = self.scores.index(new_song)
        self.current_song_properties = self.properties["items"][self.play_index]

    def get_song_properties(self):
        if self.is_album:
            URL = self.REQUEST_URL_ALBUM + self.id + "/tracks"
        else:
            URL = self.REQUEST_URL_PLAYLIST + self.id + "/tracks"
        req = requests.get(URL, headers=REQUEST_PROPERTIES)
        self.properties = req.json()
        return self.properties

    def compute_scores(self):
        self.scores = []
        if 'error' in self.properties.keys():
            return
        for song in self.properties["items"]:
            if self.is_album:
                track = Track(song["id"])
            else:
                track = Track(song["track"]["id"])
            self.scores.append(track.get_properties())
        index = random.randint(0, len(self.scores) - 1)
        self.play(self.scores[index])
        self.play_index = index
        self.current_song_properties = self.properties["items"][index]
        return self.scores

    def play(self, song):
        self.current_song = song
        self.played.append(song)

    def regenerate_token(self, code=False):
        global REQUEST_PROPERTIES
        if code:
            req = requests.post(
                "https://accounts.spotify.com/api/token",
                headers={
                    "Authorization":
                        "Basic " + os.environ.get("BASE64_ENCODED")
                },
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": "https://smartify--shadowcypher.repl.co/create_playlist"
                }
            )
            self.token = req.json()["access_token"]
            return self.token
        else:
            req = requests.post(
                "https://accounts.spotify.com/api/token",
                headers={
                    "Authorization":
                        "Basic " + os.environ.get("BASE64_ENCODED")
                },
                data={
                    "grant_type": "client_credentials"
                }
            )
            REQUEST_PROPERTIES = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer " + req.json()["access_token"],
            }
            self.token = req.json()["access_token"]
            return self.token

    def get_next(self, playlist, current_song):
        MIN_DEVIATION = 1e27
        index = 0
        components = [
            "danceability",
            "energy",
            "key",
            "speechiness",
            "valence",
            "instrumentalness"
        ]
        i = 0
        for song in self.scores:
            sum = 0
            for key, value in song.items():
                if key in components:
                    if key == "key":  # Since key is out of 10
                        sum += math.pow(
                            song[key] / 10 - current_song[key] / 10, 2)
                    else:
                        sum += math.pow(song[key] - current_song[key], 2)
            if sum < MIN_DEVIATION and song not in playlist:
                MIN_DEVIATION = sum
                index = i
            i += 1
        return self.scores[index]

    def get_similar(self):
        MIN_DEVIATION = 1e27
        index = 0
        MIN_SONG = {}
        components = [  # Whitelisted components
            "danceability", "energy", "key", "speechiness", "valence",
            "instrumentalness"
        ]
        min_song = self.get_next(self.played, self.current_song)
        self.play(MIN_SONG)
        self.current_song_properties = self.properties["items"][index]
        self.play_index = index
        self.std_dev = math.sqrt(MIN_DEVIATION)
        return min_song

    def get_queue(self):
        playlist = []
        copy_properties = self.properties["items"].copy()
        current_song = self.scores[self.play_index]
        playlist.append(current_song)
        while len(playlist) < len(copy_properties):
            next_song = self.get_next(playlist, current_song)
            playlist.append(next_song)
            current_song = next_song
        playlist = [self.properties["items"][self.scores.index(song)] for song in playlist]
        return playlist

    def get_details(self):
        req = requests.get(
            "https://api.spotify.com/v1/albums/" + self.id if self.is_album else "https://api.spotify.com/v1/playlists/" + self.id,
            headers=REQUEST_PROPERTIES)
        self.album_properties = req.json()
        return self.album_properties

    def get_album_art(self, *args):
        if self.is_album:
            req = requests.get(
                "https://api.spotify.com/v1/albums/" + self.id,
                headers=REQUEST_PROPERTIES)
            return req.json()["images"][0]
        else:
            req = requests.get(
                "https://api.spotify.com/v1/playlists/" + self.id + "/images",
                headers=REQUEST_PROPERTIES)
            return req.json()[0]
        return "https://images-na.ssl-images-amazon.com/images/I/819e05qxPEL._SL1500_.jpg"

    def get_lyrics(self):
        '''
        if self.is_album:
            title = self.current_song_properties["name"]
            artist = self.current_song_properties["artists"][0]["name"]
        else:
            title = self.current_song_properties["track"]["name"]
            artist = self.current_song_properties["track"]["artists"][0]["name"]
        
        req = requests.get("https://Lyrics-API--shadowcypher.repl.co/?title="+title+"&artist="+artist, headers={
          "API_TOKEN": os.environ.get("API_TOKEN")
        }) --> Too slow
        '''
        return {
            "lyrics": ""
        }

    def get_playlist(self):
        PLAYLIST_HEADERS = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }
        playlist = []
        copy_properties = self.properties["items"]
        index = random.randint(0, len(copy_properties) - 1)
        current_song = self.scores[index]
        playlist.append(current_song)
        while len(playlist) < len(copy_properties):
            next_song = self.get_next(playlist, current_song)
            playlist.append(next_song)
            current_song = next_song
        playlist_uri = [x["uri"] for x in playlist]
        self.get_details()
        req = requests.post(
            "https://api.spotify.com/v1/me/playlists",
            headers=PLAYLIST_HEADERS,
            data=json.dumps({
                "name": self.album_properties["name"] + " (ft. Smartify)",
                "description": "Hello World",
                "public": False
            }))
        playlist_id = req.json()["id"]
        # Batch size of 50
        return playlist_id  # Generates redirect
