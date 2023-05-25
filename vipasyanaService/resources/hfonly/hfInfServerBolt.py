import numpy as np
from scipy import signal
import time
import os
import sys
import requests
import scipy.signal as ss
from lvsdclassifier import LVSDClassifier
import storm

#******************************************#
#                 statistic                #
#******************************************#
INFAVG_URL = "http://192.168.2.132:32777/storm/timestamp/HF_InfAVG_" + str(os.getpid()) + "_"
PATIENT_NUM = 100
sumTime = 0
counter = 0

#******************************************#
#             global definition            #
#******************************************#
SYMPTOM = "HF"
SEG_LEN = 7                    # 資料長度(秒)
SAMPLE_RATE = 500               # 資料取樣率(點/秒)
TOLERANCE = 100
CHECKPOINT = "resnet18_contrastive_transfer_ECG.pth.tar"

#******************************************#
#             Server service               #
#******************************************#
def packingData(dataset):
    # dataset = [t1d1, t1d2, t1d3, t2d1, t2d2, t2d3, t3d1, t3d2, t3d3, t4d1, t4d2, t4d3, t5d1, t5d2, t5d3, t6d1, t6d2, t6d3, t7d1, t7d2, t7d3]
    # Check length first
    for txdi in dataset:
        if len(txdi) <= SAMPLE_RATE - TOLERANCE:
            return None
        elif len(txdi) != SAMPLE_RATE:
            txdi = ss.resample(txdi, SAMPLE_RATE)
    
    # Packing
    ecgDatas = []
    oneSecond = []
    leadCounter = 0
    for txdi in dataset:
        oneSecond.append(txdi)
        leadCounter = (leadCounter + 1) % 3
        if (leadCounter == 0):
            ecgDatas.append(np.array(oneSecond, dtype=np.float32))
            oneSecond = []
    
    onePersonEcgData = np.hstack(ecgDatas)
    finalEcg = [onePersonEcgData]
        
    if len(finalEcg) > 0:
        finalEcg = np.stack(finalEcg)
        finalEcg = finalEcg*1000 # V to mV
    return finalEcg

#******************************************#
#                Load Model                #
#******************************************#
lvsdClf = LVSDClassifier(CHECKPOINT)
print(time.ctime() + ' Success: HF model loading', file=sys.stderr)

class HFInfServerBolt(storm.BasicBolt):
    def process(self, tup):
        global counter
        global sumTime
        startTime = time.time()
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
        
        finalEcg = packingData([t1d1, t1d2, t1d3, t2d1, t2d2, t2d3, t3d1, t3d2, t3d3, t4d1, t4d2, t4d3, t5d1, t5d2, t5d3, t6d1, t6d2, t6d3, t7d1, t7d2, t7d3])
        
        # Check if valid data
        if (finalEcg is None):
            print(f'HF Inference fail: {patientID} finalEcg is None', file=sys.stderr)
        else:
            model_pred = lvsdClf.predict(finalEcg)
            result = int(model_pred[0])

            sumTime += (time.time() - startTime) * 1000
            counter += 1
            print(f'HF Inference success: {patientID} with result = {result}', file=sys.stderr)

            if counter % PATIENT_NUM == 0:
                requests.get(INFAVG_URL + str(round(sumTime / counter, 2)))
                sumTime = 0
                counter = 0
            storm.emit([patientID, SYMPTOM, result, t1])
        
HFInfServerBolt().run()