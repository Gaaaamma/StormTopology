import grpc
from pymongo import MongoClient
import MIInference_pb2
import MIInference_pb2_grpc
import time
import sys
#******************************************#
#               Configuration              #
#******************************************#
MONGO_ADDRESS = 'mongodb://140.113.170.152:37017/'
INF_ADDRESS = 'localhost:47777'
PATIENT = 'NCTU0002'
START_TIME = 1666096478
END_TIME   = 1666096487
DATABASE = 'ecg'
ECG_COLLECTION = 'ecg3_raw'
NUMBER_MULTIUSER = 1
nameList = []
for i in range(1,NUMBER_MULTIUSER+1):
    redundant = ''
    redundantBit = 4-len(str(i))
    for j in range(redundantBit):
        redundant+='0'
    nameList.append('PatientX_'+redundant+str(i))

client = MongoClient(MONGO_ADDRESS)
db = client[DATABASE]
ecgCollection = db[ECG_COLLECTION]
# find data in mongoDB
ecgDataList = []
query = {'Patient_CodeID':PATIENT, 'Ecg_time':{'$gte': START_TIME,'$lte':END_TIME}}
for doc in ecgCollection.find(query).sort('Ecg_time'):
    ecgDataList.append(MIInference_pb2.EcgData(timestamp=doc['Ecg_time'], diff_1=doc['Diff_1'], diff_2=doc['Diff_2'], diff_3=doc['Diff_3']))
    
def miInference(patient, startTime, endTime):
    with grpc.insecure_channel(INF_ADDRESS) as channel:
        stub = MIInference_pb2_grpc.MIInferenceStub(channel)
        request = MIInference_pb2.Input(id=patient, data=ecgDataList)
        response = stub.doInference(request)
        print('Client received: status=' + str(response.status) + ', result=' + str(response.result) +', msg=' + response.msg)
        
        # print cost time to stderr for statistic
        timeSet = str(response.msg).split(' ')
        print(f'{timeSet[0]} {timeSet[1]} {timeSet[2]} {timeSet[3]} ', file=sys.stderr)
        
def miMultiInference(num ,patient, startTime, endTime):
    # prepare multiple user (id= 1000, 1001, 1002, ...)
    patientList = []
    for i in range(0, num):
        input = MIInference_pb2.Input(id=str(1000+i), data=ecgDataList)
        patientList.append(input)

    with grpc.insecure_channel(INF_ADDRESS) as channel:
        stub = MIInference_pb2_grpc.MIInferenceStub(channel)
        request = MIInference_pb2.MultiInput(input=patientList)
        response = stub.doMultiInference(request)
        print('Client received: status=' + str(response.status) + ', result=' + str(response.result) +', msg=' + response.msg)

if __name__ == '__main__':
    # single patient inference
    if len(sys.argv) < 2:
        print('Usage: python3 miClient.py {mode}\n' +
              'Mode: 0 - single inference loop\n' +
              '      1 - multi inference once\n' +
              '      2 - both execute once\n' +
              '      3 - make ecg data mode\n')
        sys.exit()
    
    if int(sys.argv[1]) ==0:
        for i in range(0,NUMBER_MULTIUSER):
            miInference(PATIENT,START_TIME,END_TIME)
            
    elif int(sys.argv[1]) == 1:
        # multi patient inference
        miMultiInference(NUMBER_MULTIUSER, PATIENT, START_TIME, END_TIME)
        
    elif int(sys.argv[1]) == 2:
        for i in range(0,NUMBER_MULTIUSER):
            miInference(PATIENT,START_TIME,END_TIME)
            
        # multi patient inference
        miMultiInference(NUMBER_MULTIUSER, PATIENT, START_TIME, END_TIME)
    elif int(sys.argv[1]) == 3:
        for name in nameList:
            print(name,end='|')
            for doc in ecgCollection.find(query).sort('Ecg_time'):
                print(str(doc['Ecg_time']),end='&')
                print(str(doc['Diff_1']).replace(' ','') ,end='&')
                print(str(doc['Diff_2']).replace(' ',''),end='&')
                print(str(doc['Diff_3']).replace(' ',''),end='|')
            print('')
            
    else:
        print('Usage: python3 miClient.py {mode}\n' +
              'Mode: 0 - single inference loop\n' +
              '      1 - multi inference once\n' +
              '      2 - both execute once\n' +
              '      3 - make ecg data mode\n')
        sys.exit()      

# Amy|&[]&[]&[]|
