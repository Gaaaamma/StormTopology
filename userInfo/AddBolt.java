import java.util.Map;
import org.apache.storm.task.ShellBolt;
import org.apache.storm.topology.IRichBolt;
import org.apache.storm.topology.OutputFieldsDeclarer;

public class AddBolt extends ShellBolt implements IRichBolt {
    public AddBolt() {
        super("python", "addPython.py");
    }
    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // TODO Auto-generated method stub
        // declarer.declare(new Fields("word"));
    }

    @Override
    public Map<String, Object> getComponentConfiguration() {
        // TODO Auto-generated method stub
        return null;
    }
 
}