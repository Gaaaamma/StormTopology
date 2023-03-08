import storm
import sys
    
class StoreBolt(storm.BasicBolt):
    def process(self, tup):
        patientID = tup.values[0]
        symptom = tup.values[1]
        detected = tup.values[2]
        
        print("storeBolt get patientID: " + patientID, file=sys.stderr)
        print("storeBolt get symptom: " + symptom, file=sys.stderr)
        print("storeBolt get detected: " + str(detected), file=sys.stderr)

StoreBolt().run()