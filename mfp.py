#! /usr/bin/env python3

import asyncio
import bs4
import httpx
import json
import spotipy
import re
import os
import time
from collections import namedtuple

Item = namedtuple("Item", ["artist", "track"])

# So the only reason this is here is because spotify has a limit of 100 tracks
# per request ... which seems a little silly but whatever.
#
# https://chrisalbon.com/python/data_wrangling/break_list_into_chunks_of_equal_size/
# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def html(content) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(content, "html.parser")

async def subpages(client: httpx.AsyncClient, main_page: bs4.BeautifulSoup):
    for l in main_page.find(id="episodes").find_all("a"):
        if l["href"].startswith("?"):
            yield await client.get(
                "http://musicforprogramming.net/{}".format(l["href"]), timeout=10
            )

async def song_names(client: httpx.AsyncClient):
    r = await client.get("http://musicforprogramming.net/", timeout=10)
    async for p in subpages(client, html(r.content)):
        soup = html(p.content)
        for s in soup(["script", "style"]):
            s.decompose()
        for text in soup.get_text().splitlines():
            for m in re.finditer(r"(.*) - (.*)", str(text)):
                yield Item(m.group(1), m.group(2))

async def main():
    client_creds = spotipy.oauth2.SpotifyClientCredentials()
    sp_for_search = spotipy.Spotify(client_credentials_manager=client_creds)
    uris = []
    scope = "playlist-modify-private"
    user = os.getenv("SPOTIFY_USERNAME")
    token = spotipy.util.prompt_for_user_token(user, scope)
    if not token:
        raise RuntimeError("Failed to get spotify token!")
    sp = spotipy.Spotify(auth=token)
    async with httpx.AsyncClient() as client:
        async for song in song_names(client):
            # We expect this to be a JSON blob with the rough format:
            # {
            #   tracks: {
            #     items: [ { SONG INFO } ]
            #   },
            # }
            # Where SONG INFO has a URI. We assume that our search is specific 
            # enough that we'll only get a result if spotify actually has the
            # song, which is quite an assumption, and one that would take
            # upwards of an hour to verify by hand, so #%!@ that noise.
            #
            # Specifically from the song info we want the `uri`
            results = sp_for_search.search(q='artist:"{}"+track:"{}"'.format(song.artist, song.track), limit=1)
            if len(results['tracks']['items']) > 0:
                uris.append(results['tracks']['items'][0]['uri'])
    # Just use ctime as the name: not important
    playlist = sp.user_playlist_create(user, time.ctime(), public=False)
    for sublist in chunks(uris, 100):
        sp.user_playlist_add_tracks(user, playlist["id"], sublist)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
