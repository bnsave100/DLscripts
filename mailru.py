#
# * S-Name:		mailru-downloader
# * Author:		Sflashy#7643 - sflashy@mail.com
# * Date:		01/08/2021
#

import sys, zipfile, re, datetime, os
try:
    import requests
except:
    os.system('pip install requests')
    sys.exit(f'{str(datetime.datetime.now())[:-7]} INFO Please run the it again!')


class MailRu():
    def __init__(self):
        print(f'{str(datetime.datetime.now())[:-7]} INFO Initializing...')
        self.session = requests.session()
        self.weblink = re.search(r'https?\:\/\/cloud\.mail\.ru\/public\/(.*?\/.*?)\/?$', sys.argv[1]).group(1)

    def getFileNameSize(self):
        try:
            return self.session.get(f'https://cloud.mail.ru/api/v2/folder?weblink={self.weblink}').json()
        except:
            print(f'{str(datetime.datetime.now())[:-7]} ERROR Cannot connect to the \033[4mMailRu\033[0m servers.')
            sys.exit()

    def downloadFile(self):
        print(f'{str(datetime.datetime.now())[:-7]} INFO Fetching file information...')
        jsonResponse = self.getFileNameSize()
        fileName = jsonResponse['body']['name']
        fileSize = 0
        for sizes in jsonResponse['body']['list']:
            fileSize += sizes['size']
        print(f'#\n# Folder:  {fileName}\n# Size:    {int((fileSize/1024)/1024)}MB\n#')
        jsonResponse = self.session.get(f'https://cloud.mail.ru/api/v2/zip?weblink_list=["{self.weblink}"]&name={fileName}')
        print(f'{str(datetime.datetime.now())[:-7]} INFO Downloading: {fileName}.zip')
        _file = jsonResponse.json()['body']
        if not os.path.exists('./downloads'):
            os.mkdir('./downloads')
        with open(f'./downloads/{fileName}.zip', 'wb') as f:
            f.write(self.session.get(_file).content)
            self.unZipFile(fileName)

    def unZipFile(self, fileName):
        print(f'{str(datetime.datetime.now())[:-7]} INFO Unzipping file...')
        with zipfile.ZipFile(f'./downloads/{fileName}.zip', 'r') as zip_ref:
            zip_ref.extractall('./downloads/')

        print(f'{str(datetime.datetime.now())[:-7]} INFO Operation completed.')

mailru = MailRu()
mailru.downloadFile()
