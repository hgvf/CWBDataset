import numpy as np
import json
import glob
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

# 取得某個階段的所有檔名
def get_filename(root_dir):
    tmp = glob.glob(root_dir + '/*.json')
        
    return tmp

def writeTXT(z, n, e, save_path, k, w):    
    tmp = k + '_' + str(w)
    filepath = os.path.join(save_path, tmp)

    with open(filepath+'.txt', 'w') as file:
        file.write('\tZ\tN\tE\n')
        for i in range(z.shape[0]):
            file.write('\t{}\t{}\t{}\n'.format(z[i], n[i], e[i]))
    
    return filepath[15:]+'.txt'

def extractWave(p, save_path):
    save_path = os.path.join(save_path, p['event'])
    if not os.path.exists(save_path):
        #print('creating directiory: %s' %(save_path))
        os.mkdir(save_path)
    
    for k in p.keys():
        try:
            # 看測站內有多少組波形資料
            n_data = p[k]['numberOfData']
            for w in range(n_data):
                # get Z, N, E, convert to ndarray
                z, n, e = p[k][str(w)]['Z'], p[k][str(w)]['N'], p[k][str(w)]['E']
                z, n, e = np.array(z), np.array(n), np.array(e)
                
                # multiply z, n, e by factor
                z, n, e = z*p[k][str(w)]['factor'][0], n*p[k][str(w)]['factor'][1], e*p[k][str(w)]['factor'][2]
                instrument = p[k][str(w)]['instrument']
                
                # extract waveform & remove waveform from json
                waveFile = writeTXT(z, n, e, save_path, k, w)

                p[k][str(w)]['waveFile'] = waveFile
                
                del p[k][str(w)]['Z'], p[k][str(w)]['N'], p[k][str(w)]['E']
                del p[k][str(w)]['factor']
               
        except Exception as e:
#             print(e)
            pass
        
    return p
'''
if __name__ =='__main__':
    year = input('year:')
    root_path = '/mnt/nas6/CWBSN/'+year
    save_path = '/code/blog/static/blog/images/CWBSN/' + year + '/wave'
    files = get_filename(root_path)

    path = os.path.join(root_path, 'wave')
    if not os.path.exists(path):
        print('creating directiory: %s' %(path))
        os.mkdir(path)

    for file in tqdm(files):
        f = open(os.path.join(root_path, file), 'r')
        p = json.load(f)
        
        p = extractWave(p, path)
        
        # delete original json file
        os.remove(os.path.join(root_path, file))
        
        with open(os.path.join(root_path, file), 'w') as f:
            json.dump(p, f)
'''