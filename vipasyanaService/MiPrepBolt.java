import java.util.Map;
import org.apache.storm.task.ShellBolt;
import org.apache.storm.topology.IRichBolt;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.tuple.Fields;

public class MiPrepBolt extends ShellBolt implements IRichBolt {
    public MiPrepBolt() {
        super("/usr/mionlyStart.sh", "./mionly/miPrepServerBolt.py");
    }
    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // TODO Auto-generated method stub
        declarer.declare(new Fields("patientID", "seconds", 
		"t1", "t1d1", "t1d2", "t1d3",
		"t2", "t2d1", "t2d2", "t2d3",
		"t3", "t3d1", "t3d2", "t3d3",
		"t4", "t4d1", "t4d2", "t4d3",
		"t5", "t5d1", "t5d2", "t5d3",
		"t6", "t6d1", "t6d2", "t6d3",
		"t7", "t7d1", "t7d2", "t7d3",
		"t8", "t8d1", "t8d2", "t8d3",
		"t9", "t9d1", "t9d2", "t9d3",
		"t10", "t10d1", "t10d2", "t10d3"));
    }

    @Override
    public Map<String, Object> getComponentConfiguration() {
        // TODO Auto-generated method stub
        return null;
    }
 
}