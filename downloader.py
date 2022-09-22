import subprocess, requests, json, os, shutil, sys
from tqdm import tqdm


DOWNLOADURL = sys.argv[1]


class MusicDownloader():
    
    def searchDeezerUrl(self, text:str):
        searchresponse = requests.get("https://api.deezer.com/search", {"q": text})
        jsonobj = json.loads(searchresponse.text)
        try:
            return (jsonobj["data"][0]["link"])
        except:
            return (None)


    def getSpotifyPlaylistItems(self, URL:str, configfilepath:str):
        with open(configfilepath, 'r') as file:
            configfile = json.load(file)
            CLIENT_ID = configfile["SPOTIFYAUTH"]["CLIENT_ID"]
            CLIENT_SECRET = configfile["SPOTIFYAUTH"]["CLIENT_SECRET"]

        auth_response = requests.post("https://accounts.spotify.com/api/token", {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        })
        ACCESS_TOKEN = auth_response.json()['access_token']

        PLAYLIST_ID = URL.split('/').pop().split('?')[0]

        SONGS = []
        offset = 0

        playlist_data = requests.get(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks", {"offset" : offset}, headers={
            'Authorization': 'Bearer {token}'.format(token=ACCESS_TOKEN)
        }).json()
        for i in playlist_data["items"]:
            if not i["is_local"]:
                artist = i["track"]["artists"][0]["name"]
                title = i["track"]["name"]
                SONGS.append(f"{artist} {title}")
        while True:
            if not playlist_data["next"] == None:
                offset += 100
                playlist_data = requests.get(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks", {"offset" : offset}, headers={
                'Authorization': 'Bearer {token}'.format(token=ACCESS_TOKEN)
                }).json()
                for i in playlist_data["items"]:
                    if not i["is_local"]:
                        artist = i["track"]["artists"][0]["name"]
                        title = i["track"]["name"]
                        SONGS.append(f"{artist} {title}")
            else:
                break
        returnObj = []
        for i in tqdm(SONGS):
            url = self.searchDeezerUrl(i)
            if not url == None:
                returnObj.append(url)
        return returnObj

    def downloadAndZip(self, URLLIST, playlistname:str) -> str:
        if not os.path.exists("TMPplaylist"): os.mkdir("TMPplaylist")
        DOWNLOAD_DIR = f"TMPplaylist/{playlistname}"
        os.mkdir(DOWNLOAD_DIR)
        print("downloading...")
        for url in tqdm(URLLIST):
            subprocess.call(["python3","-m", "deemix","-b","128", "--path", DOWNLOAD_DIR, url], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        zipArchive = shutil.make_archive(str(playlistname), "zip", DOWNLOAD_DIR)
        #DOWNLOAD_URL = subprocess.check_output(["curl", "--upload-file", zipArchive, f"https://transfer.sh/"])
        subprocess.call(["rm", "-r", DOWNLOAD_DIR])
        return zipArchive


subprocess.call(["clear"])
downloader = MusicDownloader()
print("Matching Songs...")
playlistItems = downloader.getSpotifyPlaylistItems(DOWNLOADURL, "settings.json")
print("Start downloading songs")
file = downloader.downloadAndZip(playlistItems, "playlist")
print("Finished.")
print(file)