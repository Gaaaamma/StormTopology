import storm
import time
import sys

PATIENT_NUM = 100
counter = 0

class FakeBolt(storm.BasicBolt):
    def process(self, tup):
        global counter
        counter = (counter + 1) % PATIENT_NUM
        
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
        
        if counter == 0:
            print(f'Fake bolt get {PATIENT_NUM} tuples', file=sys.stderr)
        
FakeBolt().run()