# sdownloader
python script to download spotify playlists via deemix

### installation
``` install modules
pip3 install deemix subprocess requests json os shutil sys tqdm
```
After installing the deemix libary you have to set your ARL in the .arl file located in /home/$user/.config/deemix

Now set your Spotify Access token and Spotify Client secret in the settings.json file.

### usage
```
python3 downloader.py <spotify playlist URL>
```
