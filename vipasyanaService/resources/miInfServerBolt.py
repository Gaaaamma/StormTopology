import storm
import time
import numpy as np
from scipy import signal
from tensorflow import keras
from keras.models import load_model
from keras.optimizers import Adam
import Functions as F
import sys
import pickle
import base64

#******************************************#
#             global definition            #
#******************************************#
SYMPTOM = "MI"
SEG_LEN = 10                    # 資料長度(秒)
SAMPLE_RATE = 256               # 資料取樣率(點/秒)
TOLERANCE =5                    # check_length tolerance
MAX_MESSAGE_LENGTH = 256*1024*1024 # (Byte) equals to 256 MB

# Load model
# os.environ['CUDA_VISIBLE_DEVICES'] = '0'
MODEL_NAME = "0041-0.94762.hdf5"
model = load_model(MODEL_NAME, compile=False)  
model.compile(loss='binary_crossentropy', optimizer=Adam())
print(time.ctime() + ' Success: MI model loading', file=sys.stderr)

#******************************************#
#             other functions              #
#******************************************#
def checkLength(input_data):
    '''
    目的：針對掉封包或是取樣率不穩，來補足資料長度
    限制：最少要拿到長度2555的資料才判定有拿到完整10秒
    return: success - data with mV, fail - [(empty list)]
    '''
    dataLength = len(input_data)
    requiredLength = SEG_LEN * SAMPLE_RATE
    
    # 缺失資料點的數量超出容忍範圍
    if(dataLength < requiredLength - TOLERANCE): 
        return []
    else:
        # 在容忍範圍內補齊資料 (少的補0，多的刪除)
        input_data = np.append(input_data[:requiredLength], np.zeros( (requiredLength - dataLength) if (requiredLength - dataLength)>=0 else 0 ))

        output = input_data.flatten()
        output = signal.resample(output, requiredLength).flatten()*1000 # V -> mV
        return output

#******************************************#
#             Server service               #
#******************************************#
def doInference(patientID, x_strip_bytes, x_stft_bytes):
    timeCheckPoint = {
        'startTime': time.time(),
    }
    
    # Do mi inference
    # Inference
    x_strip = pickle.loads(x_strip_bytes)
    x_stft = pickle.loads(x_stft_bytes)
    y_score = model([x_stft,x_strip], training=False).numpy()
    output = y_score.argmax(1).flatten() # 一筆資料output為純量，多筆則為向量
    
    # Calculate time cost
    allCostTime = '{:.2f}'.format((time.time()-timeCheckPoint['startTime'])*1000)
        
    # return the result
    print(time.ctime() + ' doInference\n' +
                  '  Status: success\n' +
                  '  Patient id:  ' + patientID + '\n' +
                  '  MI result:   ' + str(output[0]) + '\n' +
                  f'  Time cost: {allCostTime} ms\n', file=sys.stderr)
    return int(output[0])
            
class MiInfServerBolt(storm.BasicBolt):
    def process(self, tup):
        patientID = tup.values[0]
        x_strip_bytes = base64.b64decode(tup.values[1].encode('utf-8'))
        x_stft_bytes = base64.b64decode(tup.values[2].encode('utf-8'))
        
        result = doInference(patientID, x_strip_bytes, x_stft_bytes)
        storm.emit([patientID, SYMPTOM, result])
        
MiInfServerBolt().run()


