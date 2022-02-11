from obspy import UTCDateTime, Stream, Trace
from datetime import datetime, timedelta
import struct, os
import numpy as np
from geopy import distance
import math

def unpackAfile(infile):
# == opening Afile ==
    b= os.path.getsize(infile)
    FH = open(infile, 'rb')
    line = FH.read(b)
    fileHeader= struct.unpack("<4s3h6bh6s", line[0:24])

    fileLength = fileHeader[3]
    port = fileHeader[10]
    FirstStn = fileHeader[11][0:4].decode('ASCII').rstrip()
    # print(fileHeader)
# =================================Header===================================

    portHeader = []
    for i in range(24,port*32,32):
        port_data = struct.unpack("<4s4s3sbh2b4s12b",line[i:i+32])
        portHeader.append(port_data)

# =================================Data===================================    

    dataStartByte = 24+int(port)*32
    dataPoint = 3*int(port)*int(fileLength)*100
    times = int(port)*3*4
    data=[]

    data = struct.unpack("<%di"%dataPoint,line[dataStartByte:dataStartByte+dataPoint*4])


    portHeader = np.array(portHeader)   
    
    data = np.array(data)
    
    idata =data.reshape((3,port,fileLength*100),order='F')

#== write to obspy Stream --
    #print(fileHeader)
    #print(len(idata[0][0]))
    sttime = UTCDateTime(fileHeader[1],fileHeader[4],fileHeader[5],fileHeader[6],fileHeader[7],fileHeader[8],fileHeader[2])
    npts = fileHeader[3]*fileHeader[9]
    samp = fileHeader[9]
    #print('fileheader[3](file_length): ', fileHeader[3])
    #print('fileheader[9](sample_rate): ', fileHeader[9])
    #print(sttime)
    
    # afst = Afile's Stream
    afst = Stream()
    multi_channel = []

    #print("fileheader[10](port): ", fileHeader[10])
    n_stn = []
    for stc in range(fileHeader[10]):
        stn = portHeader[stc][0].decode('ASCII').rstrip()
        n_stn.append(stn)
        instrument = portHeader[stc][1].decode('ASCII').rstrip()
        loc = '0'+str(portHeader[stc][6].decode('ASCII'))
        #net = "TW"
        net = str(portHeader[stc][7].decode('ASCII')).rstrip()
        GPS = int(portHeader[stc][3])

        '''
        # remove GPS unlock or broken station
        if ( GPS == 1 or GPS == 2 ):
            chc = 0
        '''

        if instrument == 'FBA':
            chc = 1
        elif instrument == 'SP':
            chc = 4
        elif instrument == 'BB':
            chc = 7

        #print(chc,instrument)
        #afst_multi = Stream()
        # for each channel in port
        for ch in range(3):
            #print(num,ch,chc)
            chn = 'Ch'+str(chc+ch)
            #print(stc,channel)

            # npts: number of sample points
            stats = {'network': net, 'station': stn, 'location': loc,
                    'channel': chn, 'npts': npts, 'sampling_rate': samp,
                    'starttime': sttime}

            data = np.array(idata[ch][stc], dtype=float)
            sttmp = Stream([Trace(data=data, header=stats)])

            afst += sttmp
            #afst_multi += sttmp
        #multi_channel.append(afst_multi)

        # break
    #stst = stms[0]
    #stst.detrend('linear').plot()
    #stms.write('test.mseed', format='MSEED')    

    # return afst, FirstStn, fileHeader
    return afst

def unpackPfile(infile):
    
    with open(infile) as f:
        lines = f.readlines()
   
    # ================================ header ================================= #
    tmp = lines[0]
    year = int(tmp[1:5])
    month = int(tmp[5:7])
    day = int(tmp[7:9])
    hour = int(tmp[9:11])
    minute = int(tmp[11:13])
    sec = float(tmp[13:19])
    lat = int(tmp[19:21])
    lat_m = float(tmp[21:26])
    lon = int(tmp[26:29])
    lon_m = float(tmp[29:34])

    lat+=lat_m/60
    lat=round(lat,2)
    lon+=lon_m/60
    lon=round(lon,2)

    dt = datetime(year,month,day,hour,minute,int(sec//1),int(sec%1 * 1000000))
    s_dt = datetime(year, month, day, hour, minute)
    depth = float(tmp[34:40])
    mag = float(tmp[40:44])
    nearest_station_distance = float(tmp[46:51])
    gap = int(tmp[51:54])
    rms = float(tmp[54:58])
    erh = float(tmp[58:62])
    erz = float(tmp[62:66])
    converge = str(tmp[66:68])
    n_phase = int(tmp[68:71])
    quality = str(tmp[71:72])

    pfile_info = {}
    pfile_info["ori_time"] = str(dt)
    pfile_info["depth"] = depth
    pfile_info["mag"] = mag
    pfile_info["lat"] = lat
    pfile_info["lon"] = lon
    pfile_info['nearest_station_dis'] = nearest_station_distance
    pfile_info['gap'] = gap
    pfile_info['rms'] = rms
    pfile_info['erh'] = erh
    pfile_info['erz'] = erz
    pfile_info['converge'] = converge
    pfile_info['n_phase'] = n_phase
    pfile_info['quality'] = quality
    # ================================ header ================================= #
    # ================================= body ================================== #
    #count = 0
    for i in lines[1:]:
        try:
            sta = i[:5].strip() # strip 去掉左右空格
            
            # dict: 裝 pfile 所有欄位
            pdict = {}
            
            # 依序裝資料進 pdict
            pdict['distance'] = float(i[6:11])
            pdict["Azimuth"] = int(i[12:15])                # 方位角
            pdict['p_emerge_angle'] = int(i[16:19])         # p-wave 射出角度
            pdict['p_polar'] = str(i[19])
            pdict['p_arrival_time'] = str(dt.replace(minute=int(i[21:23]),second=0,microsecond=0) + timedelta(seconds=float(i[23:29])))
            pdict['p_residual'] = float(i[29:34])
            pdict['p_weight'] = float(i[35:39])
            pdict['s_arrival_time'] = str(s_dt.replace(minute=int(i[21:23]), second=0, microsecond=0) + timedelta(seconds=float(i[39:45])))
            pdict['s_residual'] = float(i[45:50])
            pdict['s_weight'] = float(i[51:55])
            pdict['velocity_logA'] = float(i[55:60])
            pdict['acceleration_logA'] = float(i[60:65])
            pdict['mag_velocity'] = float(i[66:70])
            pdict['mag_acceleration'] = float(i[71:75])
           
            # P波極向若空白: +
            if pdict['p_polar'] == ' ':
                pdict['p_polar'] = '+'
                
            # s 到時有時會 = 0
            if float(i[39:45]) == 0.0:
                pdict['S'] = False
            else:
                pdict['S'] = True
                
            # intensity, pga 有時會缺漏
            try:
                pdict['intensity'] = int(i[76:77])
            except:
                pdict['intensity'] = -1
                
            try:
                pdict['pga'] = float(i[78:83])
            except:
                pdict['pga'] = -1
                
            #print(i)
            #print(pfile_info["ori_time"])
            #print(pdict)
        except Exception as e:
            pass

        pfile_info[sta] = pdict
    
    return pfile_info

def unpackPfile_2020(infile):
    
    with open(infile) as f:
        lines = f.readlines()
    
    # ================================ header ================================= #
    tmp = lines[0]
    year = int(tmp[1:5])
    month = int(tmp[5:7])
    day = int(tmp[7:9])
    hour = int(tmp[9:11])
    minute = int(tmp[11:13])
    sec = float(tmp[13:19])
    lat = int(tmp[19:21])
    lat_m = float(tmp[21:26])
    lon = int(tmp[26:29])
    lon_m = float(tmp[29:34])

    lat+=lat_m/60
    lat=round(lat,2)
    lon+=lon_m/60
    lon=round(lon,2)

    dt = datetime(year,month,day,hour,minute,int(sec//1),int(sec%1 * 1000000))
    s_dt = datetime(year, month, day, hour, minute)
    depth = float(tmp[34:40])
    mag = float(tmp[40:44])
    nearest_station_distance = float(tmp[46:51])
    gap = int(tmp[51:54])
    rms = float(tmp[54:58])
    erh = float(tmp[58:62])
    erz = float(tmp[62:66])
    converge = str(tmp[66:68])
    n_phase = int(tmp[68:71])
    quality = str(tmp[71:72])

    pfile_info = {}
    pfile_info["ori_time"] = str(dt)
    pfile_info["depth"] = depth
    pfile_info["mag"] = mag
    pfile_info["lat"] = lat
    pfile_info["lon"] = lon
    pfile_info['nearest_station_dis'] = nearest_station_distance
    pfile_info['gap'] = gap
    pfile_info['rms'] = rms
    pfile_info['erh'] = erh
    pfile_info['erz'] = erz
    pfile_info['converge'] = converge
    pfile_info['n_phase'] = n_phase
    pfile_info['quality'] = quality
    # ================================ header ================================= #
    # ================================= body ================================== #
    #count = 0
    for i in lines[1:]:
        try:
            sta = i[:5].strip() # strip 去掉左右空格
            
            # dict: 裝 pfile 所有欄位
            pdict = {}

            # 依序裝資料進 pdict
            pdict['distance'] = float(i[6:11])
            pdict["Azimuth"] = int(i[12:15])                # 方位角
            pdict['p_emerge_angle'] = str(i[16:19])         # p-wave 射出角度
            pdict['p_polar'] = str(i[19])
            pdict['p_arrival_time'] = str(dt.replace(minute=int(i[21:23]),second=0,microsecond=0) + timedelta(seconds=float(i[23:29])))
            pdict['p_residual'] = float(i[29:34])
            pdict['p_weight'] = float(i[35:39])
            pdict['s_arrival_time'] = str(s_dt.replace(minute=int(i[21:23]), second=0, microsecond=0) + timedelta(seconds=float(i[39:45])))
            pdict['s_residual'] = float(i[45:50])
            pdict['s_weight'] = float(i[51:55])
            pdict['velocity_logA'] = float(i[55:60])
            pdict['acceleration_logA'] = float(i[60:65])
            pdict['mag_velocity'] = float(i[66:70])
            pdict['mag_acceleration'] = float(i[71:75])
            
            # P波極向若空白: +
            if pdict['p_polar'] == ' ':
                pdict['p_polar'] = '+'
                
            # s 到時有時會 = 0
            if float(i[39:45]) == 0.0:
                pdict['S'] = False
            else:
                pdict['S'] = True
                
            # intensity, pga, pgv 有時會缺漏
            try:
                pdict['intensity'] = int(i[76:77])
            except:
                pdict['intensity'] = -1
           
            try:
                pdict['pga'] = float(i[78:83])
            except:
                pdict['pga'] = -1
             
            try:
                pdict['pgv'] = float(i[84:88])
            except:
                pdict['pgv'] = -1
                
            #print(i)
            #print(pfile_info["ori_time"])
            #print(pdict)
        except Exception as e:
            #print(e)
            pass

        pfile_info[sta] = pdict
    
    return pfile_info

def get_StationInfo():
    s = []
    with open('../nsta24.dat') as f:
        for line in f.readlines():
            l = line.strip().split()
           
            d = {}
            d['station'] = l[0]
            d['lon'] = float(l[1])
            d['lat'] = float(l[2])
            d['location'] = '0' + l[5]
            d['institute'] = l[6]
            d['network'] = l[7]
            d['instrument'] = l[8]
            d['E'] = float(l[9])
            d['N'] = float(l[10])
            d['Z'] = float(l[11])
            d['start'] = l[-2]
            d['end'] = l[-1]
            s.append(d)

    return s

def get_factor(my_st):
    st = my_st.copy()
    stationInfo = get_StationInfo()
    ss = []
    a_time = str(st.stats.starttime)
    a_time = a_time[:4] + a_time[5:7] + a_time[8:10]
    st_time = int(a_time)
    instrument = ''
    
    # 判斷是哪種儀器
    if st.stats.channel == 'Ch1' or st.stats.channel == 'Ch2' or st.stats.channel == 'Ch3':
        instrument = 'FBA'
    elif st.stats.channel == 'Ch4' or st.stats.channel == 'Ch5' or st.stats.channel == 'Ch6':
        instrument = 'SP'
    elif st.stats.channel == 'Ch7' or st.stats.channel == 'Ch8' or st.stats.channel == 'Ch9':
        instrument = 'BB'
                
    # 尋找相對應的測站
    for idx, s in enumerate(stationInfo):
        starttime = int(s['start'])
        end = int(s['end'])
        
        if (st_time >= starttime and st_time <= end):
            if (st.stats.station == s['station'] and instrument == s['instrument'] and st.stats.network == s['network'] and st.stats.location == s['location']):
                if st.stats.channel == 'Ch1' or st.stats.channel == 'Ch4' or st.stats.channel == 'Ch7':
                    return 'z', s['Z'], instrument       
                elif st.stats.channel == 'Ch2' or st.stats.channel == 'Ch5' or st.stats.channel == 'Ch8':
                    return 'n', s['N'], instrument
                elif st.stats.channel == 'Ch3' or st.stats.channel == 'Ch6' or st.stats.channel == 'Ch9':
                    return 'e', s['E'], instrument
    
    # 啥都沒對到
    return 'none', -1, instrument