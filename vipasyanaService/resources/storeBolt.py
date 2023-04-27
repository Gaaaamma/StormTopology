import storm
import sys
import requests

TIMESTAMP_BASE = "http://192.168.2.132:32777/storm/timestamp/"
START_TAIL = "_STO_START"
DONE_TAIL = "_STO_DONE."
PATIENT_NUM = 60
counter = {
    'MI': 0,
    'HF': 0,
    'VF': 0,
    'AF': 0
}

def countAndRequest(num, symptom):
    global counter
    counter[symptom] = (counter[symptom] + num) % PATIENT_NUM
    if (num == 1 and counter[symptom] == 1):
        # START
        response = requests.get(TIMESTAMP_BASE + symptom + START_TAIL)
    elif (num == 0 and counter[symptom] == 0):
        # DONE
        response = requests.get(TIMESTAMP_BASE + symptom + DONE_TAIL)

class StoreBolt(storm.BasicBolt):
    def process(self, tup):
        patientID = tup.values[0]
        symptom = tup.values[1]
        detected = tup.values[2]
        countAndRequest(1, symptom)
        
        print("storeBolt get patientID: " + patientID, file=sys.stderr)
        print("storeBolt get symptom: " + symptom, file=sys.stderr)
        print("storeBolt get detected: " + str(detected), file=sys.stderr)
        
        countAndRequest(0, symptom)

StoreBolt().run()