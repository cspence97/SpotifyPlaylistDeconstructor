import configparser
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import spotipy
import spotipy.oauth2 as oauth2

config = configparser.ConfigParser()
config.read('config.cfg')
client_id = config.get('SPOTIFY', 'CLIENT_ID')
client_secret = config.get('SPOTIFY', 'CLIENT_SECRET')



auth = oauth2.SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)



# Allow user to enter their desired playlist to transfer
while True:
    destination = input("Service for playlist creation: (Youtube, Apple Music) ")
    if type(destination) != str:
        continue
    elif destination.lower() == "youtube":
        youtube = True
        while True:
            playlist = input("Enter Playlist URL: ")
            if type(playlist) != str:
                continue
            break
        break
    elif destination.lower() == "apple" or destination.lower() == "apple music":
        apple = True
        while True:
            playlist = input("Enter playlist URL: ")
            if type(playlist) != str:
                continue
            break
        break


sp = spotipy.Spotify(auth.get_access_token())

songs = []

# Returns our playlist name to forward to our new playlist
results = sp.playlist(playlist)
playListTitle = results['name']
print(playListTitle)

# scans through playlist and adds songs to list
results = sp.playlist_tracks(playlist)
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

# iterates over songs to skip local files and parse song name, artist, and album for every song
for track in tracks:
    if (track['is_local']):
        tracks.remove(track)
        continue
    song = (track['track']['name'], track['track']['album']['artists'][0]['name'])
            #, track['track']['album']['name'])      #Album name ignored for youtube title purposes
    songs.append(song)

# For now we just print the songs found
# TODO implement apple music when they give you access to their API
for item in songs:
    print("(Song,      Artist,      Album)")
    print(item)



def toYoutube():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    clients_secrets_file = "client_secret_1051082308142-ugqeo2tk0idgvjim46eft2i0i6mnt0nb.apps.googleusercontent.com.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(clients_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    #Add new playlist to youtube, use spotify title
    request = youtube.playlists().insert(
        part="snippet",
        body={
            "snippet": {
                "title": playListTitle
            }
        }
    )

    response = request.execute()
    playlistID = response["id"]


    #Limit our video finding due to youtube's api quota.  Otherwise large playlists will be stuck halfway through
    #youtube api is 10,000 units a search is 100 units... Playlist insert is 50u and playlistitems insert is 50u
    # 66 songs a day
    # used some of quota in testing BYPASS THIS IF GOOGLE APPROVES QUOTA EXTENSION
    if len(songs) > 66:
        smSongs = songs[:65]
    else:
        smSongs = songs

    songIds = []

    #Searches youtube and grabs first result.  Search term is "Song Name Artist"
    #This should in 99% of cases return the proper song, unless it is not on youtube then you will need to manually trim the fat sorry
    for t in smSongs:
        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=t[0] + " " + t[1]
        )
        response = request.execute()
        songIds.append(response["items"][0]["id"]["videoId"])

    for song in songIds:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet":{
                    "playlistId": playlistID,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": song
                    }
                }
            }
        )
        response = request.execute()

if youtube:
    toYoutube()

#           Unicorn Sprinklez:    https://open.spotify.com/playlist/2doesLfLSBsRFLcGfIUiPl?lf=
