import mysql.connector
from mysql.connector import Error
import json
import os
from datetime import datetime
import numpy as np

def convertToBinaryData(filename):

    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def convertToJson(filename):

    waveform = dict() 

    with open(filename, 'r') as f: 

        lines = f.readlines() 

        data = np.array([ np.array(str.split(line)) for line in lines[1:] ]) 

        waveform["Z"] = list([float(value) for value in data[:, 0]])
        waveform["N"] = list([float(value) for value in data[:, 1]])
        waveform["E"] = list([float(value) for value in data[:, 2]])
        
        return json.dumps(waveform)

def insert(data, cursor):

    # 新增資料

    event_table_keys = ["event", "ori_time", "depth", "mag", "lat", "lon", "nearest_station_dis", "gap", "rms", "erh", "erz", "converge", "n_phase", "quality"]
    event_sql = "INSERT INTO Event (Event_Name, Event_OriginTime, Event_Depth, Event_Magnitude, Event_Longitude, Event_Latitude, Event_NearestStationDistance, Event_GAP, Event_RMS, Event_EHN, Event_ERZ, Event_Converge, Event_NPhase, Event_Quality) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    event_data = [ data[key] for key in event_table_keys ]

    cursor.execute(event_sql, tuple(event_data))

    event_id = cursor.lastrowid

    event_station_names = [x for x in list(data.keys()) if x not in event_table_keys ]
    event_station_table_keys = ["distance", "Azimuth", "p_emerge_angle", "p_polar", "p_residual", "p_weight", "s_residual", "s_weight", "velocity_logA", "acceleration_logA","mag_velocity", "mag_acceleration", "numberOfData"]
    event_station_sql = "INSERT INTO EventStation (Event_StationDistance, EventStation_Azimuth, EventStation_PEmergeAngle, EventStation_PPolar, EventStation_PResidual, EventStation_PWeight, EventStation_SResidual, EventStation_SWeight, EventStation_VelocityLogA, EventStation_AccelerationLogA, EventStatio_MagnitudeVelocity, EventStatio_MagnitudeAcceleration, EventStation_NumberOfData, Event_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    for name in event_station_names:

        event_station_data = [ data[name][key] for key in event_station_table_keys ]
        event_station_data.append(event_id)

        cursor.execute(event_station_sql, tuple(event_station_data))

        event_station_id = cursor.lastrowid
        num_data = int(data[name]["numberOfData"])

        for n in range(num_data):

            event_station_data_table_keys = ["network", "location", "sampling_rate", "starttime", "endtime", "instrument", "datatype", "pga", "pgv", "p_arrival_time", "s_arrival_time", "intensity", "waveFile"]
            event_station_data_table_available_keys = ["instrument", "intensity", "pga", "pgv", "Stime"]
            event_station_table_data_sql = "INSERT INTO EventStationData (EventStationData_Network, EventStationData_Location, EventStationData_SamplingRate, EventStationData_StartTime, EventStationData_EndTime, EventStationData_Instrument, EventStationData_Datatype, EventStationData_PGA, EventStationData_PGV, EventStationData_PArrivalTime, EventStationData_SArrivalTime, EventStationData_Intensity, EventStationData_WaveFile, EventStationData_IntensityAvailabel, EventStationData_IstrumentAvailable, EventStationData_PGAAvailable, EventStationData_PGVAvailable, EventStationData_StartTimeAvailable, EventStationData_EventStationID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            
            wave_data = [ data[name][str(n)][key] for key in event_station_data_table_keys ]

            wave_data[3] = datetime.strptime(wave_data[3],'%Y-%m-%dT%H:%M:%S.%fZ')
            wave_data[4] = datetime.strptime(wave_data[4],'%Y-%m-%dT%H:%M:%S.%fZ')
            
            wave_data_available = [ data[name][str(n)]["DataAvailable"][key] for key in event_station_data_table_available_keys ]
            wave_data = wave_data + wave_data_available
            wave_data.append(event_station_id)

            cursor.execute(event_station_table_data_sql, tuple(wave_data))

def jsons_to_mySQL(path):

    try:
        # 連接 MySQL/MariaDB 資料庫
        connection = mysql.connector.connect(
            host='140.118.127.90',          # 主機名稱
            port='3305',                    # port
            database='Seismic',             # 資料庫名稱
            user='root',                    # 帳號
            password='earthquake_123456',   # 密碼 
        )   

        cursor = connection.cursor()

        for directory, sub_directory, files in os.walk(path):

            files = [x for x in files if x.endswith(".json")]
            
            for f in files:
                try:

                    json_file = open(os.path.join(directory, f))
                    json_data = json.load(json_file)

                    insert(json_data, cursor)
            
                except Exception as e:
                    print(e)

        # 確認資料有存入資料庫
        connection.commit()

    except Error as e:
        print("資料庫連接失敗：", e)

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()

jsons_to_mySQL("D:\\Jinag\\db_client")