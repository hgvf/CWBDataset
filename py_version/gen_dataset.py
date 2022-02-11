import numpy as np
import os
import glob
import random
import json
import matplotlib.pyplot as plt
from obspy import read
from tqdm import tqdm
from calc import * 
from extractWave import *
from read_c import *

# 取得某個階段的所有檔名
def get_filename_ap(root_dir, year):
    dir = os.listdir(root_dir)

    allfile = []
    for file in dir:
        path = os.path.join(root_dir, file)
       
        tmp = glob.glob(path + '/*.P' + str(year))
        tmp1 = glob.glob(path + '/*.[1-9]' + str(year))
        allfile = allfile + tmp + tmp1
    
    return allfile

def append_afile_to_pfile(a, p):
    tmp_factor = []
    
    for a_stream in a:
        station = a_stream.stats.station
        cur_axis, factor, instrument = get_factor(a_stream)
        
        # 檢查 station 有沒有在 pfile dictionary 裡面出現
        if (station not in p.keys()) or (cur_axis == 'none'):
            continue
        #else:
        tmp_factor.append(factor)
        
        # 先取得要存進 pfile 的 data
        network = a_stream.stats.network
        location = a_stream.stats.location
        sampling_rate = a_stream.stats.sampling_rate
        starttime = str(a_stream.stats.starttime)
        endtime = str(a_stream.stats.endtime)
        channel = a_stream.stats.channel
       
        # 初始化: 讓 pfile dict 一些欄位轉成 list type
        if 'network' not in p[station].keys():
            p[station]['network'] = list()
        if 'location' not in p[station].keys():
            p[station]['location'] = list()
        if 'factor' not in p[station].keys():
            p[station]['factor'] = list()
        if 'sampling_rate' not in p[station].keys():
            p[station]['sampling_rate'] = list()
        if 'starttime' not in p[station].keys():
            p[station]['starttime'] = list()
        if 'endtime' not in p[station].keys():
            p[station]['endtime'] = list()
        if 'instrument' not in p[station].keys():
            p[station]['instrument'] = list()
        if 'datatype' not in p[station].keys():
            p[station]['datatype'] = list()

        # 加入 pfile 的 dictionary 之中
        if channel == 'Ch3' or channel == 'Ch6' or channel == 'Ch9':
            flist = tmp_factor.copy()
            p[station]['factor'].append(flist)
            p[station]['network'].append(network)
            p[station]['location'].append(location)
            p[station]['sampling_rate'].append(sampling_rate)
            p[station]['starttime'].append(starttime)
            p[station]['endtime'].append(endtime)
            p[station]['instrument'].append(instrument)
            
            if channel == 'Ch3':
                p[station]['datatype'].append('Acceleration')
            else:
                p[station]['datatype'].append('Velocity')
            
            tmp_factor.clear()
        
        # 加入 E, N, Z 進 dictionary 之中, 
        if cur_axis == 'z':
            # check if ground acceleraiont is exist
            if 'Z' not in p[station].keys():
                p[station]['Z'] = a_stream.data
            else:
                p[station]['Z'] = np.vstack([p[station]['Z'], a_stream.data])
        elif cur_axis == 'n':
            # check if ground acceleraiont is exist
            if 'N' not in p[station].keys():
                p[station]['N'] = a_stream.data
            else:
                p[station]['N'] = np.vstack([p[station]['N'], a_stream.data])
        elif cur_axis == 'e':
            # check if ground acceleraiont is exist
            if 'E' not in p[station].keys():
                p[station]['E'] = a_stream.data
            else:
                p[station]['E'] = np.vstack([p[station]['E'], a_stream.data])
       
    return p

def convert_arr_to_list(p):
    for k in p.keys():
        try:
            for sub_key in p[k].keys():
                if sub_key == 'E' or sub_key == 'N' or sub_key == 'Z': 
                    p[k][sub_key] = p[k][sub_key].tolist()
        except Exception as e:
            #print(e)
            continue
    return p

def delete_no_data(p):
    del_sta = []
    for k in p.keys():
            try:
                if ('E' not in p[k].keys()) or ('N' not in p[k].keys()) or ('Z' not in p[k].keys()):
                    del_sta.append(k)
            except:
                continue
                
    for todel in del_sta:
        del p[todel]

    return p

def copy_values(p):
    year = int(p['ori_time'][:4])
    
    for k in p.keys():
        try:
            # 篩選 key = station 
            if 'location' in p[k].keys():
                # 有幾組資料
                n_data = len(p[k]['location'])
              
                # 複製 p & s_arrival time, intensity
                p_time = p[k]['p_arrival_time']
                s_time = p[k]['s_arrival_time']
                S_avail = p[k]['S']
                intensity = p[k]['intensity']
                pga = p[k]['pga']
                
                # ============================================= #
                #     舊制的 intensirty, pga, pgv 都為 False     #
                # ============================================= #
                # check intensity, pga, pgv
                is_intensity = False
                is_pga = False
                is_pgv = False
                
                # ============================================= #
                #           檢查 intensity, pga, pgv            #
                # ============================================= #
                # 只有 2020 之後的有 pgv
                if year >= 2020:
                    pgv = p[k]['pgv']
                    del p[k]['pgv']
                    
                    p[k]['pgv'] = []
                    p[k]['isPgv'] = []
                    
                    if intensity == -1:
                        is_intensity = False
                    else:
                        is_intensity = True
                    if pga == -1 or pga == 0:
                        is_pga = False
                    else:
                        is_pga = True
                    if pgv == -1 or pgv == 0:
                        is_pgv = False
                    else:
                        is_pgv = True
                    
                    for i in range(n_data):
                        p[k]['pgv'].append(pgv)
                        p[k]['isPgv'].append(is_pgv)
                # 2019 以前都沒有 PGV，先用 nan 代替
                else:
                    p[k]['pgv'] = []
                    p[k]['isPgv'] = []
                    
                    for i in range(n_data):
                        p[k]['pgv'].append(-1)
                        p[k]['isPgv'].append(is_pgv)
                        
                # ============================================= #
                #          刪除原始欄位，改用 list 取代           #
                # ============================================= #
                del p[k]['p_arrival_time']
                del p[k]['s_arrival_time']
                del p[k]['intensity']
                del p[k]['pga']
                del p[k]['S']
                
                p[k]['p_arrival_time'] = []
                p[k]['s_arrival_time'] = []
                p[k]['intensity'] = []
                p[k]['instrument_isWork'] = []
                p[k]['pga'] = []
                p[k]['isIntensity'] = []
                p[k]['isPga'] = []
                p[k]['isStime'] = []
                
                # ============================================= #
                #       複製原始資料裡面的一些 attributes         #
                # ============================================= #
                for i in range(n_data):
                    p[k]['p_arrival_time'].append(p_time)
                    p[k]['s_arrival_time'].append(s_time)
                    p[k]['intensity'].append(intensity)
                    p[k]['instrument_isWork'].append(True)
                    p[k]['pga'].append(pga)
                    p[k]['isIntensity'].append(is_intensity)
                    p[k]['isPga'].append(is_pga)
                    p[k]['isStime'].append(S_avail)
                
        except Exception as e:
            #print(e)
            continue
            
    return p

def concat_attributes(p):
    for k in p.keys():
        try:
            # 篩選 key = station 
            if 'location' in p[k].keys():
                # ============================================= #
                #              取得數據的有效性 list             #
                # ============================================= #
                instrument = p[k]['instrument_isWork']
                intensity = p[k]['isIntensity']
                pga = p[k]['isPga']
                pgv = p[k]['isPgv']
                s = p[k]['isStime']
               
                del p[k]['instrument_isWork']
                del p[k]['isIntensity']
                del p[k]['isPga']
                del p[k]['isPgv']
                del p[k]['isStime']
                
                avail = {}
                avail['instrument'] = instrument
                avail['intensity'] = intensity
                avail['pga'] = pga
                avail['pgv'] = pgv
                avail['Stime'] = s
                p[k]['DataAvailable'] = avail
        except:
            pass
    return p

def modify_json(p, files, year):
    # 新增 primary key 欄位
    month = int(files[:2]) - 12
    month = str(month) if month//10==1 else '0'+str(month)
    version = files[-7]
    p['event'] = year[-2:] + str(month) + files[2:8] + version
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
    
    return p

def gen(files, save_base_path, sub_fname):
    for f in tqdm(range(len(files))):
        try:
            filename = files[f][:-4]
            pfile = files[f]
            num_p = files[f][-3]
            if num_p == 'P':
                num_p = '0'

            # output json file
            json_file = files[f][-12:-4] + '(' + num_p + ')' + '.json'
            save_path = os.path.join(save_base_path, json_file)

            # if repeated, don't save as json
            #if os.path.exists(save_path):
                #continue

            a = unpackAfile(filename + '.A' + sub_fname)
            if sub_fname == '20' or sub_fname == '21':
                p = unpackPfile_2020(pfile)  # 2020 ~
            else:
                p = unpackPfile(pfile)   # ~ 2019 

            # 把 afile 資訊加入 pfile's dictionary
            p = append_afile_to_pfile(a, p)

            # 把 pfile 裡面的 ndarray 轉換成 list 才能存進 dictionary
            p = convert_arr_to_list(p)    

            # 把沒有加速度資料的測站刪掉
            p = delete_no_data(p)

            # 改一些欄位
            p = copy_values(p)

            # 整合一些欄位
            p = concat_attributes(p)

            # 最後修改 json 欄位
            p = modify_json(p, json_file, sub_fname)

            # 新制震度
            p = modify(p)
            
            # 波型取出來另外存
            p = extractWave(p, wave_save_path)
            
            # write
            with open(save_path, 'w') as file:
                json.dump(p, file)
            
        except Exception as e:
            print(e)
            #pass

if __name__ == '__main__':
    #year = input('year: ')
    all_year = ['2018']

    for year in all_year:
        sub_fname = year[2:]
        base_path = '/mnt/nas6/new_CWB_data/CWB_data/' + year + '/felt'
        save_base_path = os.path.join('/mnt/nas6/CWBSN', year)
        wave_save_path = os.path.join(save_base_path, 'wave')
        files = get_filename_ap(base_path, year[-2:])
        
        # mkdir
        if not os.path.exists(save_base_path):
            print('making directory...', save_base_path)
            os.mkdir(save_base_path)
        if not os.path.exists(wave_save_path):
            print('making directory...', wave_save_path)
            os.mkdir(wave_save_path)
            
        # generate dataset
        gen(files, save_base_path, sub_fname)