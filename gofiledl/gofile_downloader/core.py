import os
import json
import http.client as http_client
import urllib.request as requests
import urllib.error as requests_error


def http_get(url: str, headers: dict = { "User-Agent": "Mozilla/5.0" }) -> bytes:
    http = requests.Request(url, headers=headers)
    response = requests.urlopen(http)
    chunk_limit = 100_000
    data = response.read(chunk_limit)
    while True:
        try:
            data += response.read(len(data)+chunk_limit)
        except http_client.IncompleteRead as e:
            data += e.partial
            continue
        else:
            break
    response.close()
    return data


def is_video(url: str) -> bool:
    for e in ("mp4", "mov", "m4v", "ts", "mkv", "avi", "wmv", "webm", "vob", "gifv", "mpg", "mpeg"):
        if url.endswith(e):
            return True
    return False


class GoFile:
    def __init__(self, api_key: str) -> None:
        if not isinstance(api_key, str) or len(api_key) < 1:
            raise ValueError("The API key must be a string.")
        self.api_key = api_key

    def fetch_resources(self, url: str) -> list:
        if not isinstance(url, str) or len(url) < 1:
            raise ValueError("The URL must be a string.")

        content_id = url[len("https://gofile.io/d/"):]
        assert len(
            content_id) > 0, "An error occured while extracting the Content ID from '" + url + "'."

        url = "https://api.gofile.io/getContent?contentId=" + content_id + "&token=" + self.api_key + "&websiteToken=websiteToken&cache=true"

        http = requests.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Accept": "*/*",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://gofile.io",
            "Connection": "keep-alive",
            "Referer": "https://gofile.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        })

        response = requests.urlopen(http)
        data = response.read()
        response.close()

        resources =  json.loads(data.decode("utf-8"))

        links = []
        contents = resources["data"]["contents"]
        for content in contents.values():
            link = content["link"]
            if link not in links:
                links.append(link)

        return links

    def download_file(self, url: str, output: str, skip_video: bool = False):
        if not isinstance(url, str) or len(url) < 1:
            raise ValueError("The URL must be a string.")

        if skip_video and is_video(url): return

        filename = url.split('/')[-1].split('?')[0]
        filename = filename.replace("%20", ' ')
        if filename in os.listdir(output): return

        try:
            opener = requests.build_opener()
            opener.addheaders = [
                ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"),
                ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"),
                ("Accept-Language", "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3"),
                ("Accept-Encoding", "gzip, deflate, br"),
                ("Connection", "keep-alive"),
                ("Cookie", "accountToken=" + self.api_key),
                ("Upgrade-Insecure-Requests", "1"),
                ("Sec-Fetch-Dest", "document"),
                ("Sec-Fetch-Mode", "navigate"),
                ("Sec-Fetch-Site", "cross-site"),
                ("Pragma", "no-cache"),
                ("Cache-Control", "no-cache"),
            ]
            requests.install_opener(opener)
            requests.urlretrieve(url, os.path.join(output, filename))

        except requests_error.ContentTooShortError:
            data = http_get(url)

            with open(os.path.join(output, filename), "wb+") as s:
                s.write(data)
            s.close()
        except requests_error.HTTPError as e:
            print(url)
            raise e
