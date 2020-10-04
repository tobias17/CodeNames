from fetch_wikidump import FetchWikidump
from preprocessors.pre_dict import PreDict
import os
from time import time
from tqdm import tqdm

LINES_PER_PART = 1000000

corp = FetchWikidump()
pre = PreDict()

def process_lines(filepath, lines):
    with open(filepath, 'w+') as file:
        first = True
        for i, line in enumerate(lines):
            clean_line = pre.clean_line(line)
            if len(clean_line) > 0:
                file.write(('\n' if not first else '') + clean_line)
                first = False

def main():
    output_folder = f'corpus/{corp.name}_{pre.name}'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    t = time()
    for fileindex, (filename, lines) in enumerate(corp.open_files()):
        print(f'loaded {filename} in {int(time() - t + 0.5)} seconds')
        threads = []
        for i in tqdm(range(int(len(lines) / LINES_PER_PART) + 1)):
            outpath = f'{output_folder}/file{fileindex}-part{i}.txt'
            if not os.path.exists(outpath):
                process_lines(outpath, lines[LINES_PER_PART*i:LINES_PER_PART*(i+1)])
        t = time()
        

if __name__ == "__main__":
    main()