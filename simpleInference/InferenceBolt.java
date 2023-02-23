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
        int t3 = tuple.getIntegerByField("t3");
        int t4 = tuple.getIntegerByField("t4");
        int t5 = tuple.getIntegerByField("t5");
        int t6 = tuple.getIntegerByField("t6");
        int t7 = tuple.getIntegerByField("t7");
        int t8 = tuple.getIntegerByField("t8");
        int t9 = tuple.getIntegerByField("t9");
        int t10 = tuple.getIntegerByField("t10");

        diff1.clear();
        diff2.clear();
        diff3.clear();

        diff1.add((List<Double>)tuple.getValueByField("t1d1"));
        diff2.add((List<Double>)tuple.getValueByField("t1d2"));
        diff3.add((List<Double>)tuple.getValueByField("t1d3"));

        diff1.add((List<Double>)tuple.getValueByField("t2d1"));
        diff2.add((List<Double>)tuple.getValueByField("t2d2"));
        diff3.add((List<Double>)tuple.getValueByField("t2d3"));

        diff1.add((List<Double>)tuple.getValueByField("t3d1"));
        diff2.add((List<Double>)tuple.getValueByField("t3d2"));
        diff3.add((List<Double>)tuple.getValueByField("t3d3"));

        diff1.add((List<Double>)tuple.getValueByField("t4d1"));
        diff2.add((List<Double>)tuple.getValueByField("t4d2"));
        diff3.add((List<Double>)tuple.getValueByField("t4d3"));

        diff1.add((List<Double>)tuple.getValueByField("t5d1"));
        diff2.add((List<Double>)tuple.getValueByField("t5d2"));
        diff3.add((List<Double>)tuple.getValueByField("t5d3"));

        diff1.add((List<Double>)tuple.getValueByField("t6d1"));
        diff2.add((List<Double>)tuple.getValueByField("t6d2"));
        diff3.add((List<Double>)tuple.getValueByField("t6d3"));

        diff1.add((List<Double>)tuple.getValueByField("t7d1"));
        diff2.add((List<Double>)tuple.getValueByField("t7d2"));
        diff3.add((List<Double>)tuple.getValueByField("t7d3"));

        diff1.add((List<Double>)tuple.getValueByField("t8d1"));
        diff2.add((List<Double>)tuple.getValueByField("t8d2"));
        diff3.add((List<Double>)tuple.getValueByField("t8d3"));

        diff1.add((List<Double>)tuple.getValueByField("t9d1"));
        diff2.add((List<Double>)tuple.getValueByField("t9d2"));
        diff3.add((List<Double>)tuple.getValueByField("t9d3"));

        diff1.add((List<Double>)tuple.getValueByField("t10d1"));
        diff2.add((List<Double>)tuple.getValueByField("t10d2"));
        diff3.add((List<Double>)tuple.getValueByField("t10d3"));

        System.out.println("Bolt get patient: " + patientID + ", with data seconds: " + String.valueOf(seconds));
        System.out.println("Data timestamps: [" + String.valueOf(t1) + ", " + String.valueOf(t2) + ", " +
        String.valueOf(t3) + ", " + String.valueOf(t4) + ", " + String.valueOf(t5) + ", " + String.valueOf(t6) + ", " +
        String.valueOf(t7) + ", " + String.valueOf(t8) + ", " + String.valueOf(t9) + ", " + String.valueOf(t10) + "]");
        
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