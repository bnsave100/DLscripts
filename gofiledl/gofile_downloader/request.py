import ssl
import http.client as http_client
import urllib.request as requests


def request(url: str, method: str = "GET", headers: dict = { "User-Agent": "Mozilla/5.0" }, data: bytes = None) -> bytes:
    http = requests.Request(url=url, method=method, data=data, headers=headers, unverifiable=True)
    response = requests.urlopen(http, context=ssl._create_unverified_context())
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

def request_file(url: str, output_path: str, headers: dict = None):
    opener = requests.build_opener()
    if headers is not None:
        opener.addheaders = [(k, v) for k, v in headers.items()]
    requests.install_opener(opener)
    requests.urlretrieve(url, output_path)
