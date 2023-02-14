FINAL_JAR = userInfo.jar
SPOUT = UserInfoSpout.class
BOLT = AddBolt.class
TOPO = DataBaseTopology.class
USER = User.class
STORM_DEP = storm-client-2.4.0.jar
JSON_DEP = gson-2.2.2.jar
PYTHON_DEP = resources

.PHONY: all clean

all: $(FINAL_JAR)

$(FINAL_JAR): $(USER) $(SPOUT) $(BOLT) $(TOPO)
	jar cvf $@ $(STORM_DEP) $(JSON_DEP) $(USER) $(SPOUT) $(BOLT) $(TOPO) $(PYTHON_DEP)

$(USER): User.java
	javac $<

$(SPOUT): UserInfoSpout.java
	javac -cp $(STORM_DEP):$(JSON_DEP):. $<

$(BOLT): AddBolt.java
	javac -cp $(STORM_DEP) $<

$(TOPO): DataBaseTopology.java $(SPOUT) $(BOLT)
	javac -cp $(STORM_DEP):. DataBaseTopology.java

clean:
	rm *.class
	rm $(FINAL_JAR)