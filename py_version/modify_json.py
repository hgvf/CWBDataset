import numpy as np
import json
import glob
import os
from tqdm import tqdm

def modify_json(files):
    for i in tqdm(range(len(files))):
        # 讀取原始 json file
        f = open(os.path.join(base_path, files[i]))
        p = json.load(f)
        
        # 新增 primary key 欄位
        month = int(files[i][:2]) - 12
        month = str(month) if month/10==1 else '0'+str(month)
        version = files[i][-7]
        p['event'] = year[-2:] + str(month) + files[i][2:8] + version
        for k in p.keys():
            try:
                if 'location' in p[k].keys():
                    # 看有幾組資料
                    n_data = len(p[k]['location'])
                    output_dict = {}
                    p[k]['numberOfData'] = n_data
                    
                    # 逐一拿出資料
                    for n in range(n_data):
                        tmp_dict = {}
                        tmp_dict['network'] = p[k]['network'][n]
                        tmp_dict['location'] = p[k]['location'][n]
                        tmp_dict['factor'] = p[k]['factor'][n]
                        tmp_dict['sampling_rate'] = p[k]['sampling_rate'][n]
                        tmp_dict['starttime'] = p[k]['starttime'][n]
                        tmp_dict['endtime'] = p[k]['endtime'][n]
                        tmp_dict['instrument'] = p[k]['instrument'][n]
                        tmp_dict['datatype'] = p[k]['datatype'][n]
                        if n_data > 1:
                            tmp_dict['Z'], tmp_dict['N'], tmp_dict['E'] = p[k]['Z'][n], p[k]['N'][n], p[k]['E'][n]
                        else:
                            tmp_dict['Z'], tmp_dict['N'], tmp_dict['E'] = p[k]['Z'], p[k]['N'], p[k]['E']
                        tmp_dict['pga'], tmp_dict['pgv'] = p[k]['pga'][n], p[k]['pgv'][n]
                        tmp_dict['p_arrival_time'], tmp_dict['s_arrival_time'] = p[k]['p_arrival_time'][n], p[k]['s_arrival_time'][n]
                        tmp_dict['intensity'] = p[k]['intensity'][n]
                        tmp_dict['DataAvailable'] = {}
                        for key in p[k]['DataAvailable'].keys():
                            tmp_dict['DataAvailable'][key] = p[k]['DataAvailable'][key][n]
                            
                        # 新增到依順序建立的新 key
                        output_dict[str(n)] = tmp_dict
                            
                    # 刪除要改掉的 keys
                    del p[k]['network'], p[k]['location'], p[k]['factor'], p[k]['sampling_rate'], p[k]['starttime']
                    del p[k]['endtime'], p[k]['instrument'], p[k]['datatype'], p[k]['Z'], p[k]['N'], p[k]['E']
                    del p[k]['pga'], p[k]['pgv'], p[k]['p_arrival_time'], p[k]['s_arrival_time']
                    del p[k]['intensity'], p[k]['DataAvailable']
                            
                    # 把改好的加進原始資料中
                    for modify_k in output_dict.keys():
                        p[k][modify_k] = output_dict[modify_k]
                        
            except Exception as e:
                #print(e)
                pass
            
        # 刪除原始 json file
        os.remove(os.path.join(base_path, files[i]))
        
        # Write into new json file
        with open(os.path.join(base_path, files[i]), 'w') as file:
            json.dump(p, file)
        


if __name__ == "__main__":
    year = input('year: ')
    
    sub_fname = year[2:]
    base_path = os.path.join('/mnt/nas6/CWBSN', year)
    files = os.listdir(base_path)
    
    modify_json(files)