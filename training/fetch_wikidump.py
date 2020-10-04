import os, json, requests, hashlib

class FetchWikidump():
    name = 'c-wikidump'

    def open_files(self):
        for (dirpath, dirnames, filenames) in os.walk(f'corpus/{self.name}'):
            for filename in filenames:
                if filename.endswith('.bz2'):
                    continue
                with open(f'{dirpath}/{filename}', encoding="utf-8") as file:
                    yield (filename, file.read().split('\n'))


WIKIDUMP_URL_PREFIX = 'https://dumps.wikimedia.org/'
WIKIDUMP_JSON_FILENAME = 'wikidump.json'
SAVE_LOCATION = f'corpus/{FetchWikidump.name}'

def create_folders():
    folders = FetchWikidump.save_location.split('/')
    for i in range(len(folders)):
        foldername = '/'.join(folders[:i+1])
        if not os.path.exists(foldername):
            os.makedirs(foldername)

def download_files(files):
    for filename in files:
        file = files[filename]
        filepath = f'{FetchWikidump.save_location}/{filename}'

        if os.path.exists(filepath):
            print(f'{filename} found, checking md5')
            md5 = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
            if md5 == file['md5']:
                print('md5 matches, skipping download')
                continue

        print(f'currently downloading {filename}...')
        r = requests.get(f'{WIKIDUMP_URL_PREFIX}{file["url"]}')
        print(f'{filename} downloaded')
        with open(filepath, 'wb+') as f:
            f.write(r.content)
        print('saved to file')


def main():
    if not os.path.exists(WIKIDUMP_JSON_FILENAME):
        print(f'please provide a {WIKIDUMP_JSON_FILENAME} file')
        return
    files = []
    with open(WIKIDUMP_JSON_FILENAME) as json_file:
        data = json.load(json_file)
        files = data['jobs']['articlesdump']['files']

    create_folders()
    download_files(files)

if __name__ == "__main__":
    main()