import numpy as np
from scipy import signal
import time
import os
import sys
import requests
import scipy.signal as ss
import storm
from VF_Inference import Model
import tensorflow as tf

#******************************************#
#                 statistic                #
#******************************************#
INFAVG_URL = "http://192.168.2.132:32777/storm/timestamp/VF_InfAVG_" + str(os.getpid()) + "_"
CALCULATE_AVG__NUM = 100
sumTime = 0
counter = 0

#******************************************#
#             global definition            #
#******************************************#
STATISTIC_MODE = True           # Emit all inference output to check throughput
SYMPTOM = "VF"
SEG_LEN = 6                    # 資料長度(秒)
SAMPLE_RATE = 500               # 資料取樣率(點/秒)
TOLERANCE = 100
CHECKPOINT = "final_model.hdf5"
TIME_EXPIRE = 60 # Data received over this time scope will reset the positive / negative record
LEAST_NEWDATA = 0 # If new time data is less than LEAST_NEWDATA => Just continue this round (Experiment accepts same data)
history = {}

#******************************************#
#                Load Model                #
#******************************************#
model = Model(CHECKPOINT)
print(time.ctime() + ' Success: VF model loading', file=sys.stderr)
print('GPU resouce usage: ' +  str(tf.test.is_gpu_available()), file=sys.stderr)

class VFInfServerBolt(storm.BasicBolt):
    def process(self, tup):
        global counter
        global sumTime
        global history
        startTime = time.time()
        patientID = tup.values[0]
        #seconds = tup.values[1]
        t1 = tup.values[2]
        #t1d1 = tup.values[3]
        t1d2 = tup.values[4]
        #t1d3 = tup.values[5]

        #t2 = tup.values[6]
        #t2d1 = tup.values[7]
        t2d2 = tup.values[8]
        #t2d3 = tup.values[9]
        
        #t3 = tup.values[10]
        #t3d1 = tup.values[11]
        t3d2 = tup.values[12]
        #t3d3 = tup.values[13]
        
        #t4 = tup.values[14]
        #t4d1 = tup.values[15]
        t4d2 = tup.values[16]
        #t4d3 = tup.values[17]
        
        #t5 = tup.values[18]
        #t5d1 = tup.values[19]
        t5d2 = tup.values[20]
        #t5d3 = tup.values[21]
        
        t6 = tup.values[22]
        #t6d1 = tup.values[23]
        t6d2 = tup.values[24]
        #t6d3 = tup.values[25]
                
        # Process history record
        if (patientID not in history) or (t6 - history[patientID]['last'] >= TIME_EXPIRE): 
            # New patient or Exceed TIME_EXPIRE
            history[patientID] = {'p': 0, 'n': 0, 'last': t6}
        elif t6 - history[patientID]['last'] < LEAST_NEWDATA : 
            # new time data is less than LEAST_NEW_DATA => Ignore this round
            print(f'VF Inference IGNORE: {patientID} with timestamp {t6} < {LEAST_NEWDATA}', file=sys.stderr)
            return 
        
        # Packing and Preprocessing
        diff2 = []
        timestampIndex = 0
        datas = [t1d2, t2d2, t3d2, t4d2, t5d2, t6d2]
        for data in datas:
            if len(data) <= SAMPLE_RATE - TOLERANCE:
                print(f'VF Inference FAIL: {patientID} data timestamp {tup.values[timestampIndex * 4 + 2]} with len {len(data)}', file=sys.stderr)
                return
            diff2_tmp = np.array(data)
            diff2.append(diff2_tmp * -1000)
            timestampIndex += 1
            
        ecg = np.concatenate(diff2)
        ecg = ss.resample(ecg, 1500).reshape(1, 1500, 1)
        _,_,spec=ss.stft(ecg,250,nperseg=250,noverlap=250-250//4,boundary=None,padded=False,axis=1)
        x = np.moveaxis(np.abs(spec),-1,1)
        stftTime = time.time()
        
        # Inference 
        y =  model.predict(x)
        predictTime = time.time()
        result = 1 if y > 0 else 0
        history[patientID]['last'] = t6

        if STATISTIC_MODE:
            sumTime += (time.time() - startTime) * 1000
            counter += 1
            print(f'VF Inference SUCCESS: {patientID} with result = {result} (STFT, Pred)=({(stftTime - startTime)*1000}ms, {(predictTime-stftTime)*1000}ms)', file=sys.stderr)

            if counter % CALCULATE_AVG__NUM == 0:
                requests.get(INFAVG_URL + str(round(sumTime / counter, 2)))
                sumTime = 0
                counter = 0
            storm.emit([patientID, SYMPTOM, result, t1])
        else:
            # Skip activation function: 'sigmoid(x) >= 0.5' is equivalent to 'x > 0'
            if y > 0:
                history[patientID]['p'] += 1
                history[patientID]['n'] = 0
            else:
                history[patientID]['n'] += 1
                history[patientID]['p'] = 0

            if history[patientID]['p'] >= 19:
                history[patientID]['p'] = 0
                print(f'VF Inference SUCCESS: {patientID} with 19 times {result}', file=sys.stderr)
                storm.emit([patientID, SYMPTOM, 1, t1])
            elif history[patientID]['n'] >= 19:
                history[patientID]['n'] = 0
                print(f'VF Inference SUCCESS: {patientID} with 19 times {result}', file=sys.stderr)
                storm.emit([patientID, SYMPTOM, 0, t1])
        
VFInfServerBolt().run()