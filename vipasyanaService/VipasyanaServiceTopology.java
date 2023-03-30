import org.apache.storm.topology.ConfigurableTopology;
import org.apache.storm.topology.TopologyBuilder;
import org.apache.storm.tuple.Fields;

 public class VipasyanaServiceTopology extends ConfigurableTopology {

    public static void main(String[] args) throws Exception {
        ConfigurableTopology.start(new VipasyanaServiceTopology(), args);
    }

    protected int run(String[] args) {
        TopologyBuilder builder = new TopologyBuilder();

        builder.setSpout("ecgdataSpout", new EcgdataSpout(), 1);
        builder.setBolt("miinfBolt", new MiInfBolt(), 4).fieldsGrouping("ecgdataSpout", new Fields("patientID"));
        // builder.setBolt("miinfBolt", new MiInfBolt(), 1).shuffleGrouping("ecgdataSpout");
        builder.setBolt("storeBolt", new StoreBolt(), 1).shuffleGrouping("miinfBolt");

        conf.setDebug(false);
        conf.setNumWorkers(6);

        String topologyName = "VipasyanaServiceTopology";
        return submit(topologyName, conf, builder);
    }
}
 