from preprocs.p_dict_v1 import PreProc
import os, json, hashlib, sys, bz2, gzip
from time import time, sleep
from tqdm import tqdm

load_location = f'../../corpus/f_wikidump'
save_location = f'{load_location}-{PreProc.name}'
index_location = f'{save_location}/index.txt'
WIKIDUMP_JSON_FILENAME = 'wikidump.json'

pre = PreProc()

def process_files(files):
    skipped = []
    if not os.path.exists(index_location):
        open(index_location, 'x')
    for filename in [key for key in files]:
        file = files[filename]
        load_filepath = f'{load_location}/{filename}'
        save_filepath = f'{save_location}/{filename[:-4]}.gz'

        with open(index_location) as f:
            found = False
            for fn in f.read().split('\n'):
                if save_filepath == fn:
                    print(f'found {filename} in index, skipping')
                    found = True
                    break
            if found:
                continue

        if os.path.exists(load_filepath):
            md5 = hashlib.md5(open(load_filepath, 'rb').read()).hexdigest()
            if not md5 == file['md5']:
                print(f'md5 does not match, skipping {filename}')
                skipped.append(filename)
                continue

        print(f'decompressing {filename}...')

        text_bytes = b''
        with open(load_filepath, 'rb') as file:
            decompressor = bz2.BZ2Decompressor()
            for data in iter(lambda : file.read(100 * 1024), b''):
                text_bytes += decompressor.decompress(data)
        print('processing...')
        text = text_bytes.decode('utf-8')

        process_lines(save_filepath, text)

def process_lines(filepath, lines):
    with gzip.open(filepath, 'wb') as file:
        first = True
        for i, line in enumerate(lines.split('\n')):
            clean_line = pre.clean_line(line)
            if len(clean_line) > 0:
                file.write((('\n' if not first else '') + clean_line).encode('UTF-8'))
                first = False
    with open(index_location, 'a+') as index:
        index.write(filepath + '\n')

def main():
    if not os.path.exists(save_location):
        os.makedirs(save_location)
    
    if not os.path.exists(WIKIDUMP_JSON_FILENAME):
        print(f'please provide a {WIKIDUMP_JSON_FILENAME} file')
        return
    files = []
    with open(WIKIDUMP_JSON_FILENAME) as json_file:
        data = json.load(json_file)
        files = data['jobs']['articlesdump']['files']

    process_files(files)

if __name__ == "__main__":
    main()