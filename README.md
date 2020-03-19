> What is this?

Running this script and following the instructions will create a Spotify playlist with a (rough approximation of) the songs that comprise [Music For Programming](http://musicforprogramming.net). This comes with two _huge_ caveats:

* We're doing song and artist name matching with no correctness guarantees: Your Mileage May Vary on if the right songs are added (it's good enough)
* Music For Programming is _not_ a set of playlists: it's a set of _mixtapes_. For example: Welcome to the Machine by Pink Floyd is in the generated playlist but appears only as a brief sample in Episode 13.

> Neat? So how do I use this?

```
$ git clone https://github.com/hgoldstein/mfp 
$ cd mfp
$ # Add SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIFY_USERNAME, and SPOTIPY_REDIRECT_URI to `.env`
$ pipenv run -- python3 mfp.py
```