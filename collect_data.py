from pandas import DataFrame
import subprocess
from glob import glob
from tqdm import tqdm
from datetime import datetime

# where to search for pictures:
root = '/home/bb/Pictures/'

def get_exif(filename):
    """Call exiftool for a filename, and extract EXIF data."""

    important_keys = ['Exposure Time', 'Rating', 'F Number', 'Lens',
                      'ISO', 'Focal Length', 'Camera Model Name', 'Create Date']

    proc = subprocess.run(['exiftool', str(filename)], stdout=subprocess.PIPE)
    exif = {}
    exif['Project'] = filename.split('/')[3]
    exif['Filename'] = filename.split('/')[-1]
    # parse exiftool output:
    try:
        for line in proc.stdout.splitlines():
            key, value = (x.strip() for x in line.decode().split(':', 1))
            if key in important_keys:
                if key == 'Exposure Time':
                    if '/' in value:
                        value = 1/int(value.split('/', 1)[1])
                    else:
                        value = float(value)
                elif key in ('Rating', 'ISO'):
                    value = int(value)
                elif key == 'F Number':
                    value = float(value)
                elif key == 'Focal Length':
                    value = float(value.split(' ', 1)[0])
                elif key == 'Create Date':
                    if '.' in value:
                        value = value.split('.', 1)[0]
                    if '+' in value:
                        value = value.split('+', 1)[0]
                    value = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                exif[key] = value
    except:
        print(filename)
    return exif

# search for these file names:
files = glob(root + '**/*.jpg') + glob(root + '**/*.JPG') + glob(root + '**/*.jpeg')
from multiprocessing import Pool

if __name__ == '__main__':
    metadata = []
    # run with 16 processes in parallel:
    with Pool(16) as p:
        metadata = list(tqdm(p.imap_unordered(get_exif, files), total=len(files), smoothing=0))

# save as pickled dataframe:
df = DataFrame(metadata)
df.to_pickle('metadata.pkl')
