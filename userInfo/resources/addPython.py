import storm
import sys
class AddPythonBolt(storm.BasicBolt):
    def process(self, tup):
        patientID = tup.values[0]
        print("PythonBolt get patientID: " + patientID, file=sys.stderr)

AddPythonBolt().run()