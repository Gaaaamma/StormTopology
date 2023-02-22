FINAL_JAR = userInfo.jar
SPOUT = EcgdataSpout.class
BOLT = AddBolt.class
TOPO = DataBaseTopology.class
ECG_RAW_DATA = EcgRawData.class
STORM_DEP = storm-client-2.4.0.jar
JSON_DEP = gson-2.2.2.jar
PYTHON_DEP = resources

.PHONY: all clean test

all: $(FINAL_JAR)

$(FINAL_JAR): $(ECG_RAW_DATA) $(SPOUT) $(BOLT) $(TOPO)
	jar cvf $@ $(STORM_DEP) $(JSON_DEP) $(ECG_RAW_DATA) $(SPOUT) $(BOLT) $(TOPO) $(PYTHON_DEP)

$(ECG_RAW_DATA): EcgRawData.java
	javac $<

$(SPOUT): EcgdataSpout.java
	javac -cp $(STORM_DEP):$(JSON_DEP):. $<

$(BOLT): AddBolt.java
	javac -cp $(STORM_DEP) $<

$(TOPO): DataBaseTopology.java $(SPOUT) $(BOLT)
	javac -cp $(STORM_DEP):. DataBaseTopology.java

test:
	javac EcgRawData.java
	javac -cp gson-2.2.2.jar:storm-client-2.4.0.jar:. Test.java
	java -cp gson-2.2.2.jar:storm-client-2.4.0.jar:. Test

clean:
	rm *.class
	rm $(FINAL_JAR)