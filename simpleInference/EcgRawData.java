import java.util.List;

public class EcgRawData {
    public List<DataObject> data;

    // Getter and setter for the data field
    // ...
    public class DataObject {
        public String Patient_CodeID;
        public int Ecg_time;
        public List<Double> Diff_1;
        public List<Double> Diff_2;
        public List<Double> Diff_3;
    }
}