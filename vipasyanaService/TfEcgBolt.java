import java.util.Map;
import org.apache.storm.task.ShellBolt;
import org.apache.storm.topology.IRichBolt;
import org.apache.storm.topology.OutputFieldsDeclarer;
// import org.apache.storm.tuple.Fields;

public class TfEcgBolt extends ShellBolt implements IRichBolt {
    public TfEcgBolt() {
        /*
         * We are now using miniconda to divide the execution environment
         * When we are under a certain conda environment 'MYENV' and execute python, we are
         * actually executing python under /home/$USER/miniconda3/envs/MYENV/bin/python
         * 
         * The reason executing tf3to12Start.sh is that we can't execute 
         * super("$HOME/...") or super("~/...") to assign python under this User
         * So the content of start.sh is to execute miniconda3/python under this User 
         */
        super("/usr/tf3to12Start.sh", "./tf3to12/tfEcgServerBolt.py");
    }
    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // TODO Auto-generated method stub
        // declarer.declare(new Fields("patientID", "symptom", "detected"));
    }

    @Override
    public Map<String, Object> getComponentConfiguration() {
        // TODO Auto-generated method stub
        return null;
    }
 
}