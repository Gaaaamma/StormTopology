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
        
        /* TF Ecg Service */
        // builder.setBolt("tfecgBolt", new TfEcgBolt(), 1).shuffleGrouping("ecgdataSpout");

        /* MI Inference Service */
        // builder.setBolt("miinfBolt", new MiInfBolt(), 2).fieldsGrouping("ecgdataSpout", new Fields("patientID"));
        // builder.setBolt("miinfBolt", new MiInfBolt(), 1).shuffleGrouping("ecgdataSpout");
        
        /* HF Inference Service */
        // builder.setBolt("hfinfBolt", new HfInfBolt(), 2).fieldsGrouping("ecgdataSpout", new Fields("patientID"));
        // builder.setBolt("hfinfBolt", new HfInfBolt(), 1).shuffleGrouping("ecgdataSpout");

        /* Vf Inference Service */
        builder.setBolt("vfinfBolt", new VfInfBolt(), 2).fieldsGrouping("ecgdataSpout", new Fields("patientID"));
        // builder.setBolt("vfinfBolt", new VfInfBolt(), 1).shuffleGrouping("ecgdataSpout");

        // builder.setBolt("storeBolt", new StoreBolt(), 1).shuffleGrouping("miinfBolt");
        // builder.setBolt("storeBolt", new StoreBolt(), 1).shuffleGrouping("hfinfBolt");
        builder.setBolt("storeBolt", new StoreBolt(), 1).shuffleGrouping("vfinfBolt");
        // builder.setBolt("storeBolt", new StoreBolt(), 1).shuffleGrouping("miinfBolt").shuffleGrouping("hfinfBolt").shuffleGrouping("vfinfBolt");

        conf.setDebug(false);
        conf.setNumWorkers(4);

        String topologyName = "VipasyanaServiceTopology";
        return submit(topologyName, conf, builder);
    }
}
 