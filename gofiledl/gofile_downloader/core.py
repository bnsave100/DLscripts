import os
import json
import hashlib
from .request import request, request_file
import urllib.error as requests_error


def is_video(url: str) -> bool:
    for e in ("mp4", "mov", "m4v", "ts", "mkv", "avi", "wmv", "webm", "vob", "gifv", "mpg", "mpeg"):
        if url.endswith(e):
            return True
    return False


class GoFile:
    def __init__(self) -> None:
        self.api_key = self.__get_api_key()

    def fetch_resources(self, url: str, password: str = None) -> list:
        if not isinstance(url, str) or url == '':
            raise ValueError("The URL must be a string.")

        if not isinstance(password, str):
            raise ValueError("The password must be a string.")

        content_id = url[len("https://gofile.io/d/"):]
        assert len(
            content_id) > 0, "An error occured while extracting the Content ID from '" + url + "'."

        url = "https://api.gofile.io/getContent?contentId=" + content_id + \
            "&token=" + self.api_key + "&websiteToken=websiteToken&cache=true"

        if password is not None and password != '':
            password = hashlib.sha256(password.encode()).hexdigest()
            url += "&password=" + password

        headers = {
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
        }
        data = request(url, headers=headers)

        resources = json.loads(data.decode("utf-8"))

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

        if skip_video and is_video(url):
            return

        filename = url.split('/')[-1].split('?')[0]
        filename = filename.replace("%20", ' ')
        if filename in os.listdir(output):
            return

        filename = os.path.join(output, filename)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie": "accountToken=" + self.api_key,
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

        try:
            request_file(url, filename, headers=headers)
        except requests_error.ContentTooShortError:
            data = request(url)

            with open(filename, "wb+") as s:
                s.write(data)
            s.close()
        except requests_error.HTTPError as e:
            print(url)
            raise e

    @staticmethod
    def __get_api_key() -> str:

        # Gets a new account token
        response = request(url="https://api.gofile.io/createAccount")
        data = json.loads(response)
        api_token = data["data"]["token"]

        # Activate the new token
        response = request(url="https://api.gofile.io/getAccountDetails?token=" + api_token)
        data = json.loads(response)
        if data["status"] != 'ok':
            raise Exception("The account was not successfully activated.")

        return api_token
