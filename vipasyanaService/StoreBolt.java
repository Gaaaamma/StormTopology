import java.util.Map;
import org.apache.storm.task.ShellBolt;
import org.apache.storm.topology.IRichBolt;
import org.apache.storm.topology.OutputFieldsDeclarer;

public class StoreBolt extends ShellBolt implements IRichBolt {
    public StoreBolt() {
        /*  Content of /usr/pystart.sh
         *  ~/.pyenv/shims/python $1 (Use python under $HOME/.pyenv to execute $1)
         *  Or /usr/bin/python $1    (Use python default version to execut $1)
         */
        super("/usr/pystart.sh", "storeBolt.py");
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