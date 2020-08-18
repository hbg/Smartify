import uuid
from django.shortcuts import render, redirect
from main.music import Track, Album
from .forms import URLForm, PlaylistForm

albums = {}


def generate_id():
    return str(uuid.uuid1())


def get_next(request):
    try:
        album = albums.get(request.session["token"])
        album.get_similar()
        score = album.scores[album.play_index]
        playlist = album.get_queue()
        if score["instrumentalness"] < 0.6:
            lyrics = album.get_lyrics()["lyrics"].split("\n")  # Gets lyrics from my own Lyrics API
        else:
            lyrics = []
        return render(request, template_name="index.html", context={
            "name": "Player",
            "description": "Smartify's song player powered by the Spotify API",
            "album_page": False,
            "song": album.current_song_properties,
            "art": album.get_album_art(),
            "token": album.token,
            "album": album.is_album,
            "deviation": round(album.std_dev, 2),
            "lyrics": lyrics,
            "queue": playlist,
            **score
            # "lyrics": genius.search_song(album.current_song_properties["name"], album.current_song_properties["artists"][0]["name"])
        })
    except Exception:
        """
        Failsafe, should never go off, but redirects in case of failure.
        """
        return redirect("/")


def get_previous(request):
    ""
    album = albums.get(request.session["token"])
    album.move_back()
    score = album.scores[album.play_index]  # Sets features to the new song's index
    playlist = album.get_queue()
    return render(request, template_name="index.html", context={
        "name": "Player",
        "description": "Smartify's song player powered by the Spotify API",
        "album_page": False,
        "song": album.current_song_properties,
        "art": album.get_album_art(),
        "token": album.token,
        "album": album.is_album,
        "danceability": score["danceability"],
        "energy": score["energy"],
        "valence": score["valence"],
        "speechiness": score["speechiness"],
        "key": score["key"],
        "instrumentalness": score["instrumentalness"],
        "deviation": round(album.std_dev, 2),
        "lyrics": [],
        "queue": playlist
        # "lyrics": genius.search_song(album.current_song_properties["name"], album.current_song_properties["artists"][0]["name"])
    })


def index(request):
    form = URLForm()
    if request.method == "POST":
        form = URLForm(request.POST)
        if form.is_valid():
            album = Album(ID=form.cleaned_data["id"], album=True)
            albums[request.session['token']] = album
            album.get_song_properties()
            album.compute_scores()
            score = album.scores[album.play_index]
            if score["instrumentalness"] < 0.6:
                lyrics = album.get_lyrics()["lyrics"].split("\n")
            else:
                lyrics = []
            playlist = album.get_queue()
            ctx = {
                "name": "Homepage",
                "description": "Smartify - The Smart Way to Listen to Music",
                "album_page": not request.method == "POST",
                "song": album.current_song_properties,
                "art": album.get_album_art(),
                "token": album.token,
                "album": True,
                "danceability": score["danceability"],
                "energy": score["energy"],
                "valence": score["valence"],
                "speechiness": score["speechiness"],
                "key": score["key"],
                "instrumentalness": score["instrumentalness"],
                "deviation": round(album.std_dev, 2),
                "lyrics": lyrics,
                "queue": playlist
            }
            return render(request, template_name="index.html", context=ctx)
    else:
        ctx = {
            "name": "Homepage",
            "description": "Welcome to Smartify - the smart way to listen to music",
            "album_page": not request.method == "POST",
            "form": form
        }
        request.session["token"] = generate_id()
        return render(request, template_name="index.html", context=ctx)


def faq(request):
    ctx = {
        "name": "Frequently Asked Questions",
        "description": "If you don't understand what Smartify is, we get it; it can be hard to understand. This page should answer your questions."
    }
    return render(request, template_name="faq.html", context=ctx)


def album(request):
    form = PlaylistForm()
    if request.method == "POST":
        form = PlaylistForm(request.POST)
        if form.is_valid():
            results = Album.find(name=form.cleaned_data["id"], is_album=True)
            ctx = {
                "name": "Results",
                "description": "Search Results | Album",
                "results": results
            }
            return render(request, template_name="album_results.html", context=ctx)
    ctx = {
        "name": "Albums",
        "description": "Find an Album on spotify",
        "type": "Album",
        "form": form
    }
    return render(request, template_name="playlists.html", context=ctx)


def search_album(request, album_id):
    album = Album(ID=album_id, album=True)
    albums[request.session['token']] = album
    album.get_song_properties()
    album.compute_scores()
    score = album.scores[album.play_index]
    if score["instrumentalness"] < 0.6:
        lyrics = album.get_lyrics()["lyrics"].split("\n")  # Gets lyrics from my own Lyrics API
    else:
        lyrics = []
    playlist = album.get_queue()
    ctx = {
        "name": "Album",
        "description": "Album Autoplay (ft. Smartify)",
        "album_page": False,
        "song": album.current_song_properties,
        "art": album.get_album_art(),
        "token": album.token,
        "album": album.is_album,
        "danceability": score["danceability"],
        "energy": score["energy"],
        "valence": score["valence"],
        "speechiness": score["speechiness"],
        "key": score["key"],
        "instrumentalness": score["instrumentalness"],
        "lyrics": lyrics,
        "queue": playlist
    }
    return render(request, template_name="index.html", context=ctx)


def search_playlist(request, playlist_id):
    album = Album(ID=playlist_id, album=False)
    albums[request.session['token']] = album
    album.get_song_properties()
    album.compute_scores()
    score = album.scores[album.play_index]
    lyrics = []
    if score["instrumentalness"] < 0.6:
        lyrics = album.get_lyrics()["lyrics"].split("\n")
    playlist = album.get_queue()
    ctx = {
        "name": "Playlist",
        "description": "Playlist Autoplay (ft. Smartify)",
        "album_page": False,
        "song": album.current_song_properties,
        "art": album.get_album_art(),
        "token": album.token,
        "album": album.is_album,
        "danceability": score["danceability"],
        "energy": score["energy"],
        "valence": score["valence"],
        "speechiness": score["speechiness"],
        "key": score["key"],
        "instrumentalness": score["instrumentalness"],
        "lyrics": lyrics,
        "queue": playlist
    }
    return render(request, template_name="index.html", context=ctx)


def playlist(request):
    form = PlaylistForm()
    if request.method == "POST":
        form = PlaylistForm(request.POST)
        if form.is_valid():
            results = Album.find(name=form.cleaned_data["id"])
            ctx = {
                "name": "Results",
                "description": "Search Results | Playlist",
                "results": results
            }
            return render(request, template_name="playlist_results.html", context=ctx)
    ctx = {
        "name": "Playlists",
        "description": "Find a Playlist on Spotify",
        "type": "Playlist",
        "form": form
    }
    return render(request, template_name="playlists.html", context=ctx)


def register_user(request):
    album = albums.get(request.session["token"])
    album.regenerate_token(code=request.GET["code"])
    playlist_id = (album.get_playlist())  # Create playlist
    return redirect("/success/" + playlist_id)


def success(request, id):
    # album = albums.get(request.session["token"])
    form = URLForm()
    ctx = {
        "name": "Homepage",
        "description": "Welcome to Smartify - the smart way to listen to music",
        "album_page": not request.method == "POST",
        "form": form,
        "playlist_id": id
    }
    return render(request, "index.html", context=ctx)
