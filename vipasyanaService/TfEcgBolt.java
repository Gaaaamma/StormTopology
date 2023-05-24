import java.util.Map;
import org.apache.storm.task.ShellBolt;
import org.apache.storm.topology.IRichBolt;
import org.apache.storm.topology.OutputFieldsDeclarer;
// import org.apache.storm.tuple.Fields;

public class TfEcgBolt extends ShellBolt implements IRichBolt {
    public TfEcgBolt() {
        /*  Content of /usr/pystart.sh
         *  ~/.pyenv/shims/python $1 (Use python under $HOME/.pyenv to execute $1)
         *  Or /usr/bin/python $1    (Use python default version to execut $1)
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