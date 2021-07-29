from bs4 import BeautifulSoup
import subprocess
import requests
import sys
import os
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

if not os.path.exists('Downloads'):
    os.mkdir("Downloads")

def soup(url):
    r = requests.get(url, headers={"User-Agent": USER_AGENT})
    return(BeautifulSoup(r.text, 'lxml'))

def download(url):
    subprocess.run(["aria2c", url, "-d", "Downloads"])
    print(f"\nDownloaded: {url}\n")

def anonfiles(link):
    dl_link = soup(link).find('a', id="download-url").get('href')
    print(f"anonfiles.com: {dl_link}")
    download(dl_link)

def evoload(link):
    form_data = {
            "code": link.split('/')[-1],
            "csrv_token": soup('https://csrv.evosrv.com/captcha').getText(),
            "pass": re.search(r"var captcha_pass = '(.*)'", str(soup('https://cd2.evosrv.com/html/jsx/e.jsx'))).group(1),
            "reff": "",
            "token": "ok"
            }
    resp = requests.post("https://evoload.io/SecurePlayer", data=form_data)
    dl_link = resp.json()["stream"]["src"]
    print(f"evoload.io: {dl_link}")
    download(dl_link)

def gofile(link):
    resp = requests.get(f"https://api.gofile.io/getFolder?folderId={link.split('/')[-1]}").json()
    key = resp['data']['childs'][0]
    dl_link = resp['data']['contents'][key]['link']
    print(f"\ngofile.io: {dl_link}\n")
    download(dl_link)

def main(inp):
    if inp.startswith('https://anonfiles.com/'):
        anonfiles(inp)
    elif inp.startswith('https://evoload.io/'):
        evoload(inp)
    elif inp.startswith('https://gofile.io/'):
        gofile(inp)
    else:
        pass

main(sys.argv[1])
