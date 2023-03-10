import storm
import sys
import requests

STORM_TIMESTAMP_START_API = "http://140.113.170.152:32777/storm/timestamp/MI_STO_START"
STORM_TIMESTAMP_DONE_API = "http://140.113.170.152:32777/storm/timestamp/MI_STO_DONE."
PATIENT_NUM = 498
count = 0

def countAndRequest(num):
    global count
    count = (count + num) % PATIENT_NUM
    if (num == 1 and count == 1):
        response = requests.get(STORM_TIMESTAMP_START_API)
    elif (num == 0 and count == 0):
        response = requests.get(STORM_TIMESTAMP_DONE_API)
    
class StoreBolt(storm.BasicBolt):
    def process(self, tup):
        countAndRequest(1)
        patientID = tup.values[0]
        symptom = tup.values[1]
        detected = tup.values[2]
        
        print("storeBolt get patientID: " + patientID, file=sys.stderr)
        print("storeBolt get symptom: " + symptom, file=sys.stderr)
        print("storeBolt get detected: " + str(detected), file=sys.stderr)
        countAndRequest(0)

StoreBolt().run()