import org.apache.storm.topology.ConfigurableTopology;
import org.apache.storm.topology.TopologyBuilder;

 public class SimpleInferenceTopology extends ConfigurableTopology {

    public static void main(String[] args) throws Exception {
        ConfigurableTopology.start(new SimpleInferenceTopology(), args);
    }

    protected int run(String[] args) {
        TopologyBuilder builder = new TopologyBuilder();

        builder.setSpout("ecgdataSpout", new EcgdataSpout(), 1);
        builder.setBolt("inferenceBolt", new InferenceBolt(), 1).shuffleGrouping("ecgdataSpout");

        conf.setDebug(false);
        conf.setNumWorkers(2);

        String topologyName = "SimpleInferenceTopology";
        return submit(topologyName, conf, builder);
    }
}
 