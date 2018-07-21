# Adds tracks to a playlist

import pprint
import sys
import spotipy
import spotipy.util as util


username = '12158815080'
playlist_id = '4eEdWa9SqJIIvJd4HpTl1Y'
scope = 'playlist-modify-public user-read-currently-playing user-read-playback-state user-modify-playback-state'
redirect='http://albertcastaned.pythonanywhere.com/callback/q'

token = util.prompt_for_user_token(username, scope,redirect_uri=redirect)

if token:
    print(token)
    sp = spotipy.Spotify(auth=token)
    #sp.trace = False
    song_name = input('Write a song name: ')
    result = sp.search(q=song_name,type='track',limit=1)
    song = [result['tracks']['items'][0]['uri']]
    print(song)
    results = sp.user_playlist_add_tracks(username, playlist_id, song)
    current_track = sp.current_user_playing_track()

    print(current_track)

else:
    print("Can't get token for", username)