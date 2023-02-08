import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Date;
import java.util.Map;

import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichBolt;
import org.apache.storm.tuple.Tuple;

public class ShowBolt extends BaseRichBolt {
    OutputCollector collector;
 
    @Override
    public void prepare(Map<String, Object> conf, TopologyContext context, OutputCollector collector) {
        this.collector = collector;
    }
 
    @Override
    public void execute(Tuple tuple) {
        String patientID = tuple.getStringByField("patientID");
        ArrayList<Integer> subStartTime = (ArrayList<Integer>) tuple.getValueByField("subStartTime");

        Timestamp time = new Timestamp((long)subStartTime.get(subStartTime.size() - 1) * 1000);
		Date date = new Date(time.getTime());  
		System.out.println("ShowBolt: " + patientID + ", Timestamp: " + subStartTime.get(subStartTime.size() - 1).toString() +", Date: " + date);
    }
 
    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // declarer.declare(new Fields("word"));
    }
 
}