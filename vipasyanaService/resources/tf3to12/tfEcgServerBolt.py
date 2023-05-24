import storm
import os
import sys
import numpy as np
import time
import argparse

from torch_model import Model3to12
from dbOperation import MongoDB

#******************************************#
#                 statistic                #
#******************************************#
INFAVG_URL = "http://192.168.2.132:32777/storm/timestamp/TF_InfAVG_" + str(os.getpid()) + "_"
CALCULATE_AVG__NUM = 100
sumTime = 0
counter = 0

#******************************************#
#                Load Model                #
#******************************************#
def args_parameter():
    parser = argparse.ArgumentParser()
    parser.add_argument('--modelPath',type=str,default='./tf3to12/step99500.ckpt.meta')
    parser.add_argument('--timeinterval',type=int,default=5)
    parser.add_argument('--SampleRate',type=int,default=256)
    parser.add_argument('--resample_len',type=int,default=500)
    parser.add_argument('--db',type=str,default='ecg')
    parser.add_argument('--history_timeinterval',type=int,default=60)
    parser.add_argument('--collection_12lead',type=str,default='ecgdata12')
    parser.add_argument('--collection_3lead',type=str,default='ecg3_raw')
    parser.add_argument('--collection_3lead_denoised',type=str,default='ecg3_denoised')
    parser.add_argument('--mongoaddress',type=str,default='mongodb://192.168.2.132:27017')
    parser.add_argument('--rpeak_time',type=int,default=5)
    parser.add_argument('--hz',type=int,default=256)
    parser.add_argument('--draw',type=int,default=0)
    parser.add_argument('--cut_sec',type=int,default=1)
    parser.add_argument('--log',type=int,default=0)
    parser.add_argument('--logFile',type=str,default='log.txt')
    parser.add_argument('--parameters',type=str,default='./tf3to12/ptbxlnorm2000mi1000vae.pt')
    parser.add_argument('--device',type=str,default='cpu')
    arg = parser.parse_args()
    return arg

args = args_parameter()
servingList = []
mongo = MongoDB(args)
model = Model3to12(args)
print(time.ctime() + ' Success: TF3to12 model loading', file=sys.stderr)

class TFEcgServerBolt(storm.BasicBolt):
    def process(self, tup):
        global counter
        global sumTime
        # startTime = time.time()
        patientID = tup.values[0]
        seconds = tup.values[1]
        
        t1 = tup.values[2]
        t1d1 = tup.values[3]
        t1d2 = tup.values[4]
        t1d3 = tup.values[5]
        
        t2 = tup.values[6]
        t2d1 = tup.values[7]
        t2d2 = tup.values[8]
        t2d3 = tup.values[9]
        
        t3 = tup.values[10]
        t3d1 = tup.values[11]
        t3d2 = tup.values[12]
        t3d3 = tup.values[13]
        
        t4 = tup.values[14]
        t4d1 = tup.values[15]
        t4d2 = tup.values[16]
        t4d3 = tup.values[17]
        
        t5 = tup.values[18]
        t5d1 = tup.values[19]
        t5d2 = tup.values[20]
        t5d3 = tup.values[21]
        
        t6 = tup.values[22]
        t6d1 = tup.values[23]
        t6d2 = tup.values[24]
        t6d3 = tup.values[25]
        
        t7 = tup.values[26]
        t7d1 = tup.values[27]
        t7d2 = tup.values[28]
        t7d3 = tup.values[29]
        
        t8 = tup.values[30]
        t8d1 = tup.values[31]
        t8d2 = tup.values[32]
        t8d3 = tup.values[33]
        
        t9 = tup.values[34]
        t9d1 = tup.values[35]
        t9d2 = tup.values[36]
        t9d3 = tup.values[37]
        
        t10 = tup.values[38]
        t10d1 = tup.values[39]
        t10d2 = tup.values[40]
        t10d3 = tup.values[41]
        
        # Packing patientInfo 
        try:
            patientInfo, exist = mongo.pack_patientInfo(patientID, t10)
            if not exist:
                print(f'Error: {patientID} does not exist in ecg.user => ignore', file=sys.stderr)
                return
        except KeyError as e:
            print(f'Error : pack_patientInfo - {e} ', file=sys.stderr)
            return
        
        # Packing ecg
        inf_in = np.array([])
        datas = [{'Ecg_time': t1, 'Diff_1': t1d1, 'Diff_2': t1d2, 'Diff_3': t1d3},
                 {'Ecg_time': t2, 'Diff_1': t2d1, 'Diff_2': t2d2, 'Diff_3': t2d3},
                 {'Ecg_time': t3, 'Diff_1': t3d1, 'Diff_2': t3d2, 'Diff_3': t3d3},
                 {'Ecg_time': t4, 'Diff_1': t4d1, 'Diff_2': t4d2, 'Diff_3': t4d3},
                 {'Ecg_time': t5, 'Diff_1': t5d1, 'Diff_2': t5d2, 'Diff_3': t5d3},
                 {'Ecg_time': t6, 'Diff_1': t6d1, 'Diff_2': t6d2, 'Diff_3': t6d3},
                 {'Ecg_time': t7, 'Diff_1': t7d1, 'Diff_2': t7d2, 'Diff_3': t7d3},
                 {'Ecg_time': t8, 'Diff_1': t8d1, 'Diff_2': t8d2, 'Diff_3': t8d3},
                 {'Ecg_time': t9, 'Diff_1': t9d1, 'Diff_2': t9d2, 'Diff_3': t9d3},
                 {'Ecg_time': t10, 'Diff_1': t10d1, 'Diff_2': t10d2, 'Diff_3': t10d3}]
        try:
            r_start_time, r_decimal, test_in = mongo.find_rr(patientInfo, datas) 
        except:
            print(f'Error: find_rr', file=sys.stderr)
            return
        
        if not r_start_time:
            if r_decimal == 0:
                print(f'Error: r_decimal == 0', file=sys.stderr)
                return
            print(f'Error: r_decimal {r_decimal} in {patientInfo["userId"]}', file=sys.stderr)
            return
        
        inf_in = test_in.reshape([1,-1,3])
                
        if inf_in.shape[0] == 0:
            print(f'Error: inf_in.shape[0] == 0', file=sys.stderr)
            return
        
        # Data_output = 
        try:
            Data_output = model.transfer(inf_in)
        except:
            print(f'Error: transfer(inf_in)', file=sys.stderr)
            return
        
        try:
            mongo.ECG_Update(patientID, Data_output)    
        except:
            print(f'Error: ECG_Update', file=sys.stderr)
            return
                
TFEcgServerBolt().run()