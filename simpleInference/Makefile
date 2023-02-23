FINAL_JAR = simpleInference.jar
SPOUT = EcgdataSpout.class
BOLT = InferenceBolt.class
BOLT_GRPC = MiGrpcBolt.class
BOLT_STORE = StoreBolt.class
TOPO = SimpleInferenceTopology.class
ECG_RAW_DATA = EcgRawData.class
DATA_OBJ = DataObject.class
STORM_DEP = storm-client-2.4.0.jar
JSON_DEP = gson-2.2.2.jar
PYTHON_DEP = resources

.PHONY: all clean test

all: $(FINAL_JAR)

$(FINAL_JAR): $(DATA_OBJ) $(ECG_RAW_DATA) $(SPOUT) $(BOLT) $(BOLT_GRPC) $(BOLT_STORE) $(TOPO)
	jar cvf $@ $(STORM_DEP) $(JSON_DEP) $(DATA_OBJ) $(ECG_RAW_DATA) $(SPOUT) $(BOLT) $(BOLT_GRPC) $(BOLT_STORE) $(TOPO) $(PYTHON_DEP)

$(DATA_OBJ): DataObject.java
	javac $<

$(ECG_RAW_DATA): EcgRawData.java
	javac $<

$(SPOUT): EcgdataSpout.java
	javac -cp $(STORM_DEP):$(JSON_DEP):. $<

$(BOLT): InferenceBolt.java
	javac -cp $(STORM_DEP) $<

$(BOLT_GRPC): MiGrpcBolt.java
	javac -cp $(STORM_DEP) $<

$(BOLT_STORE): StoreBolt.java
	javac -cp $(STORM_DEP) $<

$(TOPO): SimpleInferenceTopology.java $(SPOUT) $(BOLT)
	javac -cp $(STORM_DEP):. SimpleInferenceTopology.java

test:
	javac EcgRawData.java
	javac -cp gson-2.2.2.jar:storm-client-2.4.0.jar:. Test.java
	java -cp gson-2.2.2.jar:storm-client-2.4.0.jar:. Test

clean:
	rm *.class
	rm $(FINAL_JAR)