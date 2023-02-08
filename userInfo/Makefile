FINAL_JAR = userInfo.jar
SPOUT = UserInfoSpout.class
BOLT = ShowBolt.class
TOPO = DataBaseTopology.class
USER = User.class
STORM_DEP = storm-client-2.4.0.jar
JSON_DEP = gson-2.2.2.jar

.PHONY: all clean

all: $(FINAL_JAR)

$(FINAL_JAR): $(USER) $(SPOUT) $(BOLT) $(TOPO)
	jar cvf $@ $(STORM_DEP) $(JSON_DEP) $(USER) $(SPOUT) $(BOLT) $(TOPO)

$(USER): User.java
	javac $<

$(SPOUT): UserInfoSpout.java
	javac -cp $(STORM_DEP):$(JSON_DEP):. $<

$(BOLT): ShowBolt.java
	javac -cp $(STORM_DEP) $<

$(TOPO): DataBaseTopology.java $(SPOUT) $(BOLT)
	javac -cp $(STORM_DEP):. DataBaseTopology.java

clean:
	rm *.class
	rm $(FINAL_JAR)