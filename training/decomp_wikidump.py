import os, json, hashlib, sys, bz2

WIKIDUMP_JSON_FILENAME = 'wikidump.json'
SAVE_LOCATION = 'corpus/c-wikidump'

def decompress_files(files):
    skipped = []
    for filename in [key for key in files]:
        file = files[filename]
        filepath = f'{SAVE_LOCATION}/{filename}'
        new_filepath = filepath[:-4]

        if os.path.exists(new_filepath):
            print(f'{filename} already exists')
            continue

        if os.path.exists(filepath):
            md5 = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
            if not md5 == file['md5']:
                print(f'md5 does not match, skipping {filename}')
                skipped.append(filename)
                continue

        print(f'decompressing {filename}...')
        with open(new_filepath, 'wb+') as new_file, open(filepath, 'rb') as file:
            decompressor = bz2.BZ2Decompressor()
            for data in iter(lambda : file.read(100 * 1024), b''):
                new_file.write(decompressor.decompress(data))


def main():
    if not os.path.exists(WIKIDUMP_JSON_FILENAME):
        print(f'please provide a {WIKIDUMP_JSON_FILENAME} file')
        return
    files = []
    with open(WIKIDUMP_JSON_FILENAME) as json_file:
        data = json.load(json_file)
        files = data['jobs']['articlesdump']['files']

    decompress_files(files)

if __name__ == "__main__":
    main()