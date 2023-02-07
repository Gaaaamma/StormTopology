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
        String data = tuple.getStringByField("data");
        System.out.println("ShowBolt: " + data);
    }
 
    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // declarer.declare(new Fields("word"));
    }
 
}