import storm
import sys

num = 0
def testFun():
    print("HELLOWORLD: " + str(num), file=sys.stderr)
    
class InfBolt(storm.BasicBolt):
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

num += 1000
testFun()
InfBolt().run()