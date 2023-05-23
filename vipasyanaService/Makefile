FINAL_JAR = vipasyanaService.jar
SPOUT = EcgdataSpout.class
BOLT_TF_ECG = TfEcgBolt.class
BOLT_MI_PREP = MiPrepBolt.class
BOLT_MI_INF = MiInfBolt.class
BOLT_HF_INF = HfInfBolt.class
BOLT_VF_INF = VfInfBolt.class
BOLT_STORE = StoreBolt.class
TOPO = VipasyanaServiceTopology.class
ECG_RAW_DATA = EcgRawData.class
DATA_OBJ = DataObject.class
STORM_DEP = storm-client-2.4.0.jar
JSON_DEP = gson-2.2.2.jar
PYTHON_DEP = resources

.PHONY: all clean test

all: $(FINAL_JAR)

$(FINAL_JAR): $(DATA_OBJ) $(ECG_RAW_DATA) $(SPOUT) $(BOLT_TF_ECG) $(BOLT_MI_PREP) $(BOLT_MI_INF) $(BOLT_HF_INF) $(BOLT_VF_INF) $(BOLT_STORE) $(TOPO)
	jar cvf $@ $(STORM_DEP) $(JSON_DEP) $(DATA_OBJ) $(ECG_RAW_DATA) $(SPOUT) $(BOLT_TF_ECG) $(BOLT_MI_PREP) $(BOLT_MI_INF) $(BOLT_HF_INF) $(BOLT_VF_INF) $(BOLT_STORE) $(TOPO) $(PYTHON_DEP)

$(DATA_OBJ): DataObject.java
	javac $<

$(ECG_RAW_DATA): EcgRawData.java
	javac $<

$(SPOUT): EcgdataSpout.java
	javac -cp $(STORM_DEP):$(JSON_DEP):. $<

$(BOLT_TF_ECG): TfEcgBolt.java
	javac -cp $(STORM_DEP) $<

$(BOLT_MI_PREP): MiPrepBolt.java
	javac -cp $(STORM_DEP) $<

$(BOLT_MI_INF): MiInfBolt.java
	javac -cp $(STORM_DEP) $<

$(BOLT_HF_INF): HfInfBolt.java
	javac -cp $(STORM_DEP) $<

$(BOLT_VF_INF): VfInfBolt.java
	javac -cp $(STORM_DEP) $<

$(BOLT_STORE): StoreBolt.java
	javac -cp $(STORM_DEP) $<

$(TOPO): VipasyanaServiceTopology.java
	javac -cp $(STORM_DEP):. VipasyanaServiceTopology.java

test:
	javac EcgRawData.java
	javac -cp gson-2.2.2.jar:storm-client-2.4.0.jar:. Test.java
	java -cp gson-2.2.2.jar:storm-client-2.4.0.jar:. Test

clean:
	rm *.class
	rm $(FINAL_JAR)