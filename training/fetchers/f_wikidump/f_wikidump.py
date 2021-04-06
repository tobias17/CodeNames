import os, json, requests, hashlib

name = 'f_wikidump'
save_location = f'../../corpus/{name}'
WIKIDUMP_URL_PREFIX = 'https://dumps.wikimedia.org/'
WIKIDUMP_JSON_FILENAME = 'wikidump.json'

def open_files():
    for (dirpath, dirnames, filenames) in os.walk(f'corpus/{name}'):
        for filename in filenames:
            if filename.endswith('.bz2'):
                continue
            with open(f'{dirpath}/{filename}', encoding="utf-8") as file:
                yield (filename, file.read().split('\n'))

def get_filepath(filename):
    return f'{save_location}/{filename}'

def check_hash(filepath, file):
    md5 = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
    return md5 == file['md5']

def download_files(files):
    for filename in files:
        file = files[filename]
        filepath = get_filepath(filename)

        if os.path.exists(filepath):
            print(f'{filename} found, checking md5')
            if check_hash(filepath, file):
                print('md5 matches, skipping download')
                continue

        print(f'downloading {filename}...')
        r = requests.get(f'{WIKIDUMP_URL_PREFIX}{file["url"]}')
        print(f'{filename} downloaded, {r}')

        with open(filepath, 'wb+') as f:
            f.write(r.content)
        print(f'saved to file, {"hash matches" if check_hash(filepath, file) else "HASH ERROR"}')

    correct = 0
    for filename in files:
        if check_hash(get_filepath(filename), files[filename]):
            correct += 1
    print(f'Finished downloading, {correct}/{len(files)} hashes match')

def main():
    if not os.path.exists(WIKIDUMP_JSON_FILENAME):
        print(f'please provide a {WIKIDUMP_JSON_FILENAME} file')
        return
    files = []
    with open(WIKIDUMP_JSON_FILENAME) as json_file:
        data = json.load(json_file)
        files = data['jobs']['articlesdump']['files']

    if not os.path.exists(save_location):
        os.makedirs(save_location)
    download_files(files)

if __name__ == "__main__":
    main()