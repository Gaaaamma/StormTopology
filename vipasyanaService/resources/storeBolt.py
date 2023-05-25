import storm
import sys
import requests

WRITE_BACK_TO_DB = True
SYMPTOM_RECORD = "http://192.168.2.132:32777/record/symptom/ai"
TIMESTAMP_BASE = "http://192.168.2.132:32777/storm/timestamp/"
START_TAIL = "_STO_START"
DONE_TAIL = "_STO_DONE."
PATIENT_NUM = 100
record = {}
counter = {
    'MI': 0,
    'HF': 0,
    'VF': 0,
    'AF': 0
}

def countAndRequest(num, symptom):
    global counter
    counter[symptom] = (counter[symptom] + num) % PATIENT_NUM
    if (num == 0 and counter[symptom] == 0):
        # DONE
        response = requests.get(TIMESTAMP_BASE + symptom + DONE_TAIL)

def statusModification(id, symptom, detect, timestamp):
    payload = {
        "id": id,
        "symptom": symptom,
        "timestamp": timestamp,
        "detect": detect
    }
    response = requests.post(SYMPTOM_RECORD, json=payload)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Status changed: ({id}, {symptom}, {detect}, {timestamp})", file=sys.stderr)
    else:
        print(f"Error: symptom record failed with status_code {response.status_code}", file=sys.stderr)

class StoreBolt(storm.BasicBolt):
    def process(self, tup):
        global record
        patientID = tup.values[0]
        symptom = tup.values[1]
        detected = tup.values[2]
        timestamp = tup.values[3]
        
        countAndRequest(1, symptom)
        
        if WRITE_BACK_TO_DB:
            if patientID in record:
                oldStatus = record[patientID][symptom]
                record[patientID][symptom] = detected
                if detected != oldStatus:
                    statusModification(patientID, symptom, detected, timestamp)
            else:
                record[patientID] = {'MI': 0, 'HF': 0, 'VF': 0, 'AF': 0}
                record[patientID][symptom] = int(detected)
                statusModification(patientID, symptom, detected, timestamp)
        
        print(f"storeBolt get info: ({patientID}, {symptom}, {detected}, {timestamp})", file=sys.stderr)

        countAndRequest(0, symptom)

StoreBolt().run()