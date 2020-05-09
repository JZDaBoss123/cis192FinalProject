'''
Name: Akshay Sharma and Jonathan Zein
PennKey: aksharma
Hours of work required:
'''

from flask import Flask, redirect, url_for, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIFY_CLIENT_ID = "ea9c663491c24f0385d3f6bccc24b0ad"
SPOTIFY_CLIENT_SECRET = "38d10dc3a32d4f18b88a68988fa71931"

client_credentials = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials)

app = Flask(__name__)
global_cache = {}  # cache to store POST requests, cannot handle concurrent connections as of now


class Recommendations:
    def __init__(self, mood, genre, energy, num_songs):
        self.mood = mood
        self.genre = genre
        self.energy = energy
        self.num_songs = num_songs

    def generate_recommendations(self):
        valence = self.get_valence()
        tgt_genre = self.genre

        all_genres = sp.recommendation_genre_seeds()

        if self.genre not in all_genres['genres']:
            return None
        else:
            return sp.recommendations(seed_genres=[tgt_genre], country="US", target_valence=valence,
                                      target_energy=self.energy)

    def get_valence(self):
        tgt_valence = 0
        if self.mood is "happy":
            tgt_valence = 0.8
        elif self.mood is "romantic":
            tgt_valence = 0.7
        elif self.mood is "nervous":
            tgt_valence = 0.6
        elif self.mood is "mad":
            tgt_valence = 0.4
        elif self.mood is "sad":
            tgt_valence = 0.2

        return tgt_valence


@app.route('/')
def home():
    return redirect(url_for('starter_page'))


@app.route('/preferences', methods=["GET", "POST"])
def starter_page():
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        result = request.form
        if 'genre' and 'mood' and 'energy' not in global_cache:
            global_cache['genre'] = str.lower(result['genreInput'])
            global_cache['mood'] = str.lower(result['moodInput'])
            global_cache['energy'] = str.lower(result['energyInput'])
        else:
            global_cache['genre'] = str.lower(result['genreInput'])
            global_cache['mood'] = str.lower(result['moodInput'])
            global_cache['energy'] = str.lower(result['energyInput'])

    return redirect(url_for('output_song'))


def generate_recommendation():
    tgt_genre = global_cache['genre']
    tgt_mood = global_cache['mood']
    tgt_energy = global_cache['energy']

    recommendations = Recommendations(tgt_mood, tgt_genre, tgt_energy, 1)
    result = recommendations.generate_recommendations()

    song_dictionary = {}
    if result:
        for track in result['tracks'][: 10]:
            song = track['name']
            artist = track['album']['artists'][0]['name']
            song_dictionary[song] = artist

    return song_dictionary


@app.route("/song")
def output_song():
    song_dictionary = generate_recommendation()

    song_list = list(song_dictionary.keys())
    artist_list = list(song_dictionary.values())

    if request.method == "GET":
        return render_template("rec.html", songName=song_list[0])


if __name__ == '__main__':
    app.run(debug=True)
