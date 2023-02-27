import storm
import sys
import grpc
import MIInference_pb2
import MIInference_pb2_grpc

INF_ADDRESS = "localhost:47777"
SYMPTOM = "MI"
def miInference(patient, ecgData):
    with grpc.insecure_channel(INF_ADDRESS) as channel:
        stub = MIInference_pb2_grpc.MIInferenceStub(channel)
        request = MIInference_pb2.Input(id=patient, data=ecgData)
        response = stub.doInference(request)
        print('Client received: status=' + str(response.status) + ', result=' + str(response.result) +', msg=' + response.msg, file=sys.stderr)
        
        # print cost time to stderr for statistic
        timeSet = str(response.msg).split(' ')
        print(f'{timeSet[0]} {timeSet[1]} {timeSet[2]} {timeSet[3]} ', file=sys.stderr)
        return [response.status, response.result]   
        
def miMultiInference(num, ecgData):
    # prepare multiple user (id= 1000, 1001, 1002, ...)
    inputList = []
    for i in range(0, num):
        input = MIInference_pb2.Input(id=str(1000+i), data=ecgData)
        inputList.append(input)

    with grpc.insecure_channel(INF_ADDRESS) as channel:
        stub = MIInference_pb2_grpc.MIInferenceStub(channel)
        request = MIInference_pb2.MultiInput(input=inputList)
        response = stub.doMultiInference(request)
        print('Client received: status=' + str(response.status) + ', result=' + str(response.result) +', msg=' + response.msg, file=sys.stderr)

class MiInfBolt(storm.BasicBolt):
    def process(self, tup):
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
        print("infBolt get patientID: " + patientID, file=sys.stderr)
        print("infBolt get seconds: " + str(seconds), file=sys.stderr)
        print("infBolt get timestamps: [" + str(t1) + ", " + str(t2) + ", " 
              + str(t3) + ", " + str(t4) + ", " + str(t5) + ", " + str(t6) + ", " 
              + str(t7) + ", " + str(t8) + ", " + str(t9) + ", " + str(t10) + "]", file=sys.stderr)
        print("infBolt get type: ", type(t1d1), file=sys.stderr)
        print("infBolt get t1 len: (" + str(len(t1d1)) + "," + str(len(t1d2)) + "," + str(len(t1d3)) + ")", file=sys.stderr)
        
        # Send data to MI Server via gRPC
        # 10 secs data is valid
        if  (t1 != 0 and t2 != 0 and t3 != 0 and t4 != 0 and t5 != 0 and 
             t6 != 0 and t7 != 0 and t8 != 0 and t9 != 0 and t10 != 0):
            # Pack one patient data
            ecgData = [MIInference_pb2.EcgData(timestamp = t1, diff_1 = t1d1, diff_2 = t1d2, diff_3 = t1d3),
                       MIInference_pb2.EcgData(timestamp = t2, diff_1 = t2d1, diff_2 = t2d2, diff_3 = t2d3),
                       MIInference_pb2.EcgData(timestamp = t3, diff_1 = t3d1, diff_2 = t3d2, diff_3 = t3d3),
                       MIInference_pb2.EcgData(timestamp = t4, diff_1 = t4d1, diff_2 = t4d2, diff_3 = t4d3),
                       MIInference_pb2.EcgData(timestamp = t5, diff_1 = t5d1, diff_2 = t5d2, diff_3 = t5d3),
                       MIInference_pb2.EcgData(timestamp = t6, diff_1 = t6d1, diff_2 = t6d2, diff_3 = t6d3),
                       MIInference_pb2.EcgData(timestamp = t7, diff_1 = t7d1, diff_2 = t7d2, diff_3 = t7d3),
                       MIInference_pb2.EcgData(timestamp = t8, diff_1 = t8d1, diff_2 = t8d2, diff_3 = t8d3),
                       MIInference_pb2.EcgData(timestamp = t9, diff_1 = t9d1, diff_2 = t9d2, diff_3 = t9d3),
                       MIInference_pb2.EcgData(timestamp = t10, diff_1 = t10d1, diff_2 = t10d2, diff_3 = t10d3)]
            rtnList = miInference(patientID, ecgData)
            
            # Check rtn status
            if (rtnList[0] == 1):
                storm.emit([patientID, SYMPTOM, int(rtnList[1])])
            else:
                storm.emit([patientID, SYMPTOM, -2])
        else:
            storm.emit([patientID, SYMPTOM, -1])
            
MiInfBolt().run()