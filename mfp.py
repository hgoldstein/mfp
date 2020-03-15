#! /usr/bin/env python3

import asyncio
import bs4
import httpx
import json
import re


async def get_subpages(client: httpx.AsyncClient, main_page: bs4.BeautifulSoup):
    for l in main_page.find(id="episodes").find_all("a"):
        if l["href"].startswith("?"):
            yield await client.get(
                "http://musicforprogramming.net/{}".format(l["href"]), timeout=10
            )


async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://musicforprogramming.net/", timeout=10)
        songs = []
        async for p in get_subpages(
            client, bs4.BeautifulSoup(r.content, "html.parser")
        ):
            soup = bs4.BeautifulSoup(p.content, "html.parser")
            for s in soup(["script", "style"]):
                s.decompose()
            for text in soup.get_text().splitlines():
                for s in re.findall(r".* - .*", str(text)):
                    songs.append(s)
        print(json.dumps(songs))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
