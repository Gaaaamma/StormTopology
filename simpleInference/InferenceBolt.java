import java.util.ArrayList;
import java.util.Map;
import java.util.List;
import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichBolt;
import org.apache.storm.tuple.Tuple;

public class InferenceBolt extends BaseRichBolt {
    OutputCollector collector;
    List<List<Double>> diff1;
	List<List<Double>> diff2;
	List<List<Double>> diff3;

    @Override
    public void prepare(Map<String, Object> topoConf, TopologyContext context, OutputCollector collector) {
        // TODO Auto-generated method stub
        this.collector = collector;
        this.diff1 = new ArrayList<>();
	    this.diff2 = new ArrayList<>();
	    this.diff3 = new ArrayList<>();
    }

    @Override
    public void execute(Tuple tuple) {
        // TODO Auto-generated method stub
        String patientID = tuple.getStringByField("patientID");
        int seconds = tuple.getIntegerByField("seconds");
        int t1 = tuple.getIntegerByField("t1");
        int t2 = tuple.getIntegerByField("t2");
        diff1.clear();
        diff2.clear();
        diff3.clear();

        diff1.add((List<Double>)tuple.getValueByField("t1d1"));
        diff2.add((List<Double>)tuple.getValueByField("t1d2"));
        diff3.add((List<Double>)tuple.getValueByField("t1d3"));

        diff1.add((List<Double>)tuple.getValueByField("t2d1"));
        diff2.add((List<Double>)tuple.getValueByField("t2d2"));
        diff3.add((List<Double>)tuple.getValueByField("t2d3"));

        System.out.println("Bolt get patient: " + patientID + ", with data seconds: " + String.valueOf(seconds));
        System.out.println("Data timestamps: " + String.valueOf(t1) + ", " + String.valueOf(t2));
        System.out.println("Diff1.size(): " + String.valueOf(diff1.size()));
        System.out.println("Diff2.size(): " + String.valueOf(diff2.size()));
        System.out.println("Diff3.size(): " + String.valueOf(diff3.size()));
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // TODO Auto-generated method stub
        // ....
    }
}