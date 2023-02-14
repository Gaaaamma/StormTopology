import org.apache.storm.topology.ConfigurableTopology;
import org.apache.storm.topology.TopologyBuilder;

 public class DataBaseTopology extends ConfigurableTopology {

    public static void main(String[] args) throws Exception {
        ConfigurableTopology.start(new DataBaseTopology(), args);
    }

    protected int run(String[] args) {
        TopologyBuilder builder = new TopologyBuilder();

        builder.setSpout("userInfo", new UserInfoSpout(), 1);
        builder.setBolt("addBolt", new AddBolt(), 1).shuffleGrouping("userInfo");

        conf.setDebug(true);
        conf.setNumWorkers(2);

        String topologyName = "DataBaseTopology";
        return submit(topologyName, conf, builder);
    }
}
 