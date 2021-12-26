import os
import json
from gofile_downloader import GoFile


global config
config = json.load(open("config.json"))


def main(gofile_url: str, password: str = ''):
    output = os.path.join('./', 'downloads/')

    if not os.path.exists(output):
        os.mkdir(output)

    # Handle the folder name to create the output path.
    folder_name = gofile_url.split('/')[-1].split('?')[0]
    output = os.path.join(output, folder_name)
    meta_output = os.path.join(output, "meta.json")
    if not os.path.exists(output):
        os.mkdir(output)
        json.dump([], open(meta_output, 'a'))

    # Dumps out media links.
    api = GoFile()

    resources = json.load(open(meta_output))
    if len(resources) == 0:
        resources = api.fetch_resources(gofile_url, password)
        json.dump(resources, open(meta_output, "w+"))

    output = os.path.join(output, "files/")
    if not os.path.exists(output):
        os.mkdir(output)

    for resource in resources:
        api.download_file(resource, output)


if __name__ == "__main__":
    main(config["URL"], config["PASSWORD"])
