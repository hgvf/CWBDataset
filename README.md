# CWBDataset

### Files
| Files | Function |
|:-----:|:--------:|
| read_c | 讀取 Afile, Pfile |
| gen_dataset | 產生以事件為單位的 json 檔 |
| calc | 計算新制數據，修改 json 檔 |
| gen_waveform | 從 Dataset 挑出可訓練波形 |



### Json 檔內部格式 (左: Header, 右: Station)
| Key | Attribute | Key | Attribute |                               
|:--------------------:|:---------------:|:----------------:|:----------:|                              
| ori_time             | 地震發生時間      | distance         | 與震央距離  |
| depth                | 地震深度         | Azimuth          | 方位角      | 
| mag                  | 地震規模         | p_emerge_angle   | P波射出角度  |
| lat                  | 震央緯度(北緯: +) | p_polar          | P波極向     |
| lon                  | 震央經度(東經: +) | p_residual       | P波到時殘差  |
| nearest_station_dis  | 最近震央之測站距離 | p_weight         | P波權重     |
| gap                  | 最大空餘角 GAP    | s_residual       | S波到時殘差 |
| rms                  | RMS 走時殘差     | s_weight          | S波權重    |
| erh                  | ERH 水平誤差     | velocity_logA     | 速度 logA  |
| erz                  | ERZ 水平誤差     | acceleration_logA | 加速度 logA |
| converge             | 收斂(F,X,-)      | mag_velocity      | 速度規模    |
| n_phase              | 相位數           | mag_acceleration   | 加速度規模  |
| quality              | 定位品質(A~D)    | network           | 地震網      |
| x| x                                   | location          | 儀器位置(1:地表, 2:井下)|
| x| x                                   | factor            | 轉換量 (Z, N, E) |
| x| x                                   | sampling_rate     | 取樣率      |
| x| x                                   | starttime         | 儀器開始時間 |
| x| x                                   | endtime           | 儀器結束時間 |
| x| x                                   | instrument        | 儀器種類    |
| x| x                                   | datatype          | 波形種類(Velocity, Acceleration)|
| x| x                                   | Z, N, E           | Z, N, E 軸的波形資料 |
| x| x                                   | pga, pgv          | PGA, PGV  |
| x| x                                   | p_arrival_time    | P波到時     |
| x| x                                   | s_arrival_time    | S波到時     |
| x| x                                   | intensity         | 震度        |
| x| x                                   | DataAvailable     | Attribute 是否有效(T, F) |
