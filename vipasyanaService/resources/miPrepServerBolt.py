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
class EcgData:
    def __init__(self, timestamp, diff_1, diff_2, diff_3):
        self.timestamp = timestamp
        self.diff_1 = diff_1
        self.diff_2 = diff_2
        self.diff_3 = diff_3

class Input:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        
def doInference(request):
    timeCheckPoint = {
        'startTime': time.time(),
        'packTime': 0,
        'preprocessTime': 0,
    }
    diff_1 = []
    diff_2 = []
    diff_3 = []

    # Parsing Input data
    for data in request.data:
        diff_1.extend(data.diff_1)
        diff_2.extend(data.diff_2)
        diff_3.extend(data.diff_3)
    diff1RawLength = str(len(diff_1))
    diff2RawLength = str(len(diff_2))
    diff3RawLength = str(len(diff_3))
    diff_1 = checkLength(diff_1)
    diff_2 = checkLength(diff_2)
    diff_3 = checkLength(diff_3)
    timeCheckPoint['packTime'] = time.time()

    if(len(diff_1) ==0 or len(diff_2)==0 or len(diff_3) ==0):
        #invalid length of input data
        print(time.ctime() + ' doInference\n' +
            '  Patient id: ' + request.id + '\n' + 
            '  Data length: ' + str(len(request.data)) + '\n' +
            '  Diff_1 length: ' + diff1RawLength + '\n' +
            '  Diff_2 length: ' + diff2RawLength + '\n' +
            '  Diff_3 length: ' + diff3RawLength + '\n' +
            '  Time cost: ' + '{:.2f}'.format((time.time()-timeCheckPoint['startTime'])*1000) + ' ms\n', file=sys.stderr)
        return [0, 0, 0]
    
    else:
        # Preprocessing
        x = np.stack([diff_1,diff_2,diff_3], axis=-1).reshape(-1,2560,3) # 預設為一次一個人做檢測
        x_strip = F.make_2d_temp(x, verbose=0)
        x_stft = F.stft(x, fs=256, step=25)[:,:,1:92,:]
        x_strip_bytes = base64.b64encode(pickle.dumps(x_strip)).decode('utf-8')
        x_stft_bytes = base64.b64encode(pickle.dumps(x_stft)).decode('utf-8')
        timeCheckPoint['preprocessTime'] = time.time()

        # Calculate time cost
        packCostTime = '{:.2f}'.format((timeCheckPoint['packTime']-timeCheckPoint['startTime'])*1000)
        preprocessCostTime = '{:.2f}'.format((timeCheckPoint['preprocessTime']-timeCheckPoint['packTime'])*1000)
        allCostTime = '{:.2f}'.format((time.time()-timeCheckPoint['startTime'])*1000)
            
        # return the result
        print(time.ctime() + ' doInference\n' +
                      '  Status: success\n' +
                      '  Patient id:  ' + request.id + '\n' +
                      '  Data length: ' + str(len(request.data)) + '\n' +
                      '  Data start:  ' + str(request.data[0].timestamp) + '\n' +
                      '  Data end:    ' + str(request.data[len(request.data)-1].timestamp) + '\n' +
                      '  Diff_1 length: ' + diff1RawLength + '\n' +
                      '  Diff_2 length: ' + diff2RawLength + '\n' +
                      '  Diff_3 length: ' + diff3RawLength + '\n' +
                      f'  Pack cost: {packCostTime} ms\n' +
                      f'  PreP cost: {preprocessCostTime} ms\n' +
                      f'  Time cost: {allCostTime} ms\n', file=sys.stderr)
        return [1, x_strip_bytes, x_stft_bytes]
        
class MiInfServerBolt(storm.BasicBolt):
    def process(self, tup):
        patientID = tup.values[0]
        seconds = tup.values[1]
        t1 = tup.values[2]
        t1d1 = tup.values[3]
        t1d2 = tup.values[4]
        t1d3 = tup.values[5]
        data1 = EcgData(t1, t1d1, t1d2, t1d3)
        
        t2 = tup.values[6]
        t2d1 = tup.values[7]
        t2d2 = tup.values[8]
        t2d3 = tup.values[9]
        data2 = EcgData(t2, t2d1, t2d2, t2d3)
        
        t3 = tup.values[10]
        t3d1 = tup.values[11]
        t3d2 = tup.values[12]
        t3d3 = tup.values[13]
        data3 = EcgData(t3, t3d1, t3d2, t3d3)
        
        t4 = tup.values[14]
        t4d1 = tup.values[15]
        t4d2 = tup.values[16]
        t4d3 = tup.values[17]
        data4 = EcgData(t4, t4d1, t4d2, t4d3)
        
        t5 = tup.values[18]
        t5d1 = tup.values[19]
        t5d2 = tup.values[20]
        t5d3 = tup.values[21]
        data5 = EcgData(t5, t5d1, t5d2, t5d3)
        
        t6 = tup.values[22]
        t6d1 = tup.values[23]
        t6d2 = tup.values[24]
        t6d3 = tup.values[25]
        data6 = EcgData(t6, t6d1, t6d2, t6d3)
        
        t7 = tup.values[26]
        t7d1 = tup.values[27]
        t7d2 = tup.values[28]
        t7d3 = tup.values[29]
        data7 = EcgData(t7, t7d1, t7d2, t7d3)
        
        t8 = tup.values[30]
        t8d1 = tup.values[31]
        t8d2 = tup.values[32]
        t8d3 = tup.values[33]
        data8 = EcgData(t8, t8d1, t8d2, t8d3)
        
        t9 = tup.values[34]
        t9d1 = tup.values[35]
        t9d2 = tup.values[36]
        t9d3 = tup.values[37]
        data9 = EcgData(t9, t9d1, t9d2, t9d3)
        
        t10 = tup.values[38]
        t10d1 = tup.values[39]
        t10d2 = tup.values[40]
        t10d3 = tup.values[41]
        data10 = EcgData(t10, t10d1, t10d2, t10d3)
        
        input = Input(patientID, [data1, data2, data3, data4, data5, data6, data7, data8, data9, data10])
        result = doInference(input)
        if (result[0] != 0):
            storm.emit([patientID, result[1], result[2]])
        
MiInfServerBolt().run()


