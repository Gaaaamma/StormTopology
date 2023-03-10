import storm
import sys
import requests

STORM_TIMESTAMP_START_API = "http://140.113.170.152:32777/storm/timestamp/MI_STO_START"
STORM_TIMESTAMP_DONE_API = "http://140.113.170.152:32777/storm/timestamp/MI_STO_DONE."
PATIENT_START = "NCTU0000_0"
PATIENT_END = "NCTU0002_99"

class StoreBolt(storm.BasicBolt):
    def process(self, tup):
        patientID = tup.values[0]
        if (patientID == PATIENT_START):
            response = requests.get(STORM_TIMESTAMP_START_API)
        symptom = tup.values[1]
        detected = tup.values[2]
        
        print("storeBolt get patientID: " + patientID, file=sys.stderr)
        print("storeBolt get symptom: " + symptom, file=sys.stderr)
        print("storeBolt get detected: " + str(detected), file=sys.stderr)
        
        if (patientID == PATIENT_END):
            response = requests.get(STORM_TIMESTAMP_DONE_API)

StoreBolt().run()