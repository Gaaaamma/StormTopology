import org.apache.storm.topology.ConfigurableTopology;
import org.apache.storm.topology.TopologyBuilder;
import org.apache.storm.tuple.Fields;

 public class SimpleInferenceTopology extends ConfigurableTopology {

    public static void main(String[] args) throws Exception {
        ConfigurableTopology.start(new SimpleInferenceTopology(), args);
    }

    protected int run(String[] args) {
        TopologyBuilder builder = new TopologyBuilder();

        builder.setSpout("ecgdataSpout", new EcgdataSpout(), 1);
        // builder.setBolt("migrpcBolt", new MiGrpcBolt(), 1).shuffleGrouping("ecgdataSpout");
        // builder.setBolt("miinfBolt", new MiInfBolt(), 1).shuffleGrouping("ecgdataSpout");
        builder.setBolt("miinfBolt", new MiInfBolt(), 2).fieldsGrouping("ecgdataSpout", new Fields("patientID"));
        // builder.setBolt("inferenceBolt", new InferenceBolt(), 1).shuffleGrouping("ecgdataSpout");
        builder.setBolt("storeBolt", new StoreBolt(), 1).shuffleGrouping("miinfBolt");

        conf.setDebug(false);
        conf.setNumWorkers(4);

        String topologyName = "SimpleInferenceTopology";
        return submit(topologyName, conf, builder);
    }
}
 