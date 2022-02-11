import numpy as np
import json
import glob
import os
from tqdm import tqdm

# 取得某個階段的所有檔名
def get_filename(root_dir):
    tmp = glob.glob(root_dir + '/*.json')
        
    return tmp

if __name__ == '__main__':
    year = input('year: ')
    root = "/mnt/nas6/CWBSN/"+year
    files = get_filename(root)

    for file in tqdm(files):
        f = open(os.path.join(root, file), 'r')
        p = json.load(f)
        
        month = int(file[-16:-14])-12
        month = str(month) if month//10==1 else '0'+str(month)
        pk = year[-2:]+month+file[-14:-8]+file[-7]
        p['event'] = pk
    
        os.remove(os.path.join(root, file))
        with open(os.path.join(root, file), 'w') as f:
            json.dump(p, f)