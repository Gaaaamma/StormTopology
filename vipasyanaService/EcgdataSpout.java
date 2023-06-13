import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

import org.apache.storm.spout.SpoutOutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichSpout;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Values;
import org.apache.storm.utils.Utils;
import com.google.gson.Gson;

 public class EcgdataSpout extends BaseRichSpout {
    SpoutOutputCollector spoutOutputCollector;
	boolean latencyTest = false;
	int testTimes = 5;
	int[] testCounts = {1,2,5,10,50,100,150,200,300};
	Map<Integer, Float> testResults = new HashMap<>();

	int period = 1000;
	String apiRequest = "http://192.168.2.132:32777/users/ecg/rawdata/";
	int seconds = 10;
	int counts = 1;
	Gson gson;

    @Override
    public void open(Map<String, Object> conf, TopologyContext context, SpoutOutputCollector collector) {
        // TODO Auto-generated method stub
        this.spoutOutputCollector = collector;
		this.gson = new Gson();
    }

    @Override
    public void nextTuple() {
        // TODO Auto-generated method stub
		if (latencyTest) {
			LatencyTester();
			for (int i = 0; i < testCounts.length ; i++) {
				if (testResults.containsKey(testCounts[i])) {
					Float value = testResults.get(testCounts[i]);
					System.out.println("Counts: " + testCounts[i] + " => " + value + " ms => " + (value / testCounts[i]) + " ms/one");
				} else {
					System.out.println("Lack result counts: " + testCounts[i]);
				}
			}
			latencyTest = false;
		}
        Utils.sleep(period);
        try { 
            String target = apiRequest + String.valueOf(seconds) + "/" + String.valueOf(counts);
			Gson gson = new Gson();
			EcgRawData rawData = gson.fromJson(httpRequest("GET", target, target), EcgRawData.class);

			String patient = "";
			int timestampIndex = 0;
			int[] timestamps = new int[seconds];
			Arrays.fill(timestamps, 0);
			List<List<Double>> diff1 = new ArrayList<>();
			List<List<Double>> diff2 = new ArrayList<>();
			List<List<Double>> diff3 = new ArrayList<>();
			for (int i = 0; i < rawData.data.size(); i++) {
				if (rawData.data.get(i).Patient_CodeID.equals(patient)) {
					// Same patient => append data
					// Check timestamp to see which index we are going to insert
					int timeDiff = rawData.data.get(i).Ecg_time - timestamps[timestampIndex - 1];
					while (timeDiff > 1) {
						timestamps[timestampIndex] = 0;
						timestampIndex++;
						timeDiff--;
						diff1.add(new ArrayList<>());
						diff2.add(new ArrayList<>());
						diff3.add(new ArrayList<>());
					}
					timestamps[timestampIndex] = rawData.data.get(i).Ecg_time;
					timestampIndex++;
					diff1.add(rawData.data.get(i).Diff_1);
					diff2.add(rawData.data.get(i).Diff_2);
					diff3.add(rawData.data.get(i).Diff_3);

				} else {
					// New Patient => Emit old patient if patient != ""
					if (!patient.equals("")) {
						// Emit old patients
						// If diffI.size != seconds => Padding
						int difference1 = seconds - diff1.size();
						int difference2 = seconds - diff2.size();
						int difference3 = seconds - diff3.size();
						while (difference1 > 0) {
							diff1.add(new ArrayList<>());
							difference1--;
						}
						while (difference2 > 0) {
							diff2.add(new ArrayList<>());
							difference2--;
						}
						while (difference3 > 0) {
							diff3.add(new ArrayList<>());
							difference3--;
						}

						// Emit
						this.spoutOutputCollector.emit(new Values(patient, seconds, 
						timestamps[0], diff1.get(0), diff2.get(0), diff3.get(0),
						timestamps[1], diff1.get(1), diff2.get(1), diff3.get(1),
						timestamps[2], diff1.get(2), diff2.get(2), diff3.get(2),
						timestamps[3], diff1.get(3), diff2.get(3), diff3.get(3),
						timestamps[4], diff1.get(4), diff2.get(4), diff3.get(4),
						timestamps[5], diff1.get(5), diff2.get(5), diff3.get(5),
						timestamps[6], diff1.get(6), diff2.get(6), diff3.get(6),
						timestamps[7], diff1.get(7), diff2.get(7), diff3.get(7),
						timestamps[8], diff1.get(8), diff2.get(8), diff3.get(8),
						timestamps[9], diff1.get(9), diff2.get(9), diff3.get(9)));

						// System.out.println("A: ");
						// System.out.println(patient);
						// for (int j = 0; j < diff1.size(); j++) {
						// 	System.out.println(timestamps[j]);
						// }
						// System.out.println(diff1.size() + " : " + diff2.size() + " : " + diff3.size());
					}
					// Initialize
					timestampIndex = 0;
					Arrays.fill(timestamps, 0);
					diff1.clear();
					diff2.clear();
					diff3.clear();

					// Pack New Patient 
					patient = rawData.data.get(i).Patient_CodeID;
					timestamps[timestampIndex] = rawData.data.get(i).Ecg_time;
					timestampIndex++;
					diff1.add(rawData.data.get(i).Diff_1);
					diff2.add(rawData.data.get(i).Diff_2);
					diff3.add(rawData.data.get(i).Diff_3);
				}
			}

			// Emit last parent data
			if (!patient.equals("")) {
				// Emit old patients
				// If diffI.size != seconds => Padding
				int difference1 = seconds - diff1.size();
				int difference2 = seconds - diff2.size();
				int difference3 = seconds - diff3.size();
				while (difference1 > 0) {
					diff1.add(new ArrayList<>());
					difference1--;
				}
				while (difference2 > 0) {
					diff2.add(new ArrayList<>());
					difference2--;
				}
				while (difference3 > 0) {
					diff3.add(new ArrayList<>());
					difference3--;
				}
				
				// Emit
				this.spoutOutputCollector.emit(new Values(patient, seconds, 
				timestamps[0], diff1.get(0), diff2.get(0), diff3.get(0),
				timestamps[1], diff1.get(1), diff2.get(1), diff3.get(1),
				timestamps[2], diff1.get(2), diff2.get(2), diff3.get(2),
				timestamps[3], diff1.get(3), diff2.get(3), diff3.get(3),
				timestamps[4], diff1.get(4), diff2.get(4), diff3.get(4),
				timestamps[5], diff1.get(5), diff2.get(5), diff3.get(5),
				timestamps[6], diff1.get(6), diff2.get(6), diff3.get(6),
				timestamps[7], diff1.get(7), diff2.get(7), diff3.get(7),
				timestamps[8], diff1.get(8), diff2.get(8), diff3.get(8),
				timestamps[9], diff1.get(9), diff2.get(9), diff3.get(9)));

				// System.out.println("B: ");
				// System.out.println(patient);
				// for (int j = 0; j < diff1.size(); j++) {
				// 	System.out.println(timestamps[j]);
				// }				
				// System.out.println(diff1.size() + " : " + diff2.size() + " : " + diff3.size());
			}

        } catch (Exception e) {
			System.out.println("Spout exception: " + e);
        }
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        // TODO Auto-generated method stub
        declarer.declare(new Fields("patientID", "seconds", 
		"t1", "t1d1", "t1d2", "t1d3",
		"t2", "t2d1", "t2d2", "t2d3",
		"t3", "t3d1", "t3d2", "t3d3",
		"t4", "t4d1", "t4d2", "t4d3",
		"t5", "t5d1", "t5d2", "t5d3",
		"t6", "t6d1", "t6d2", "t6d3",
		"t7", "t7d1", "t7d2", "t7d3",
		"t8", "t8d1", "t8d2", "t8d3",
		"t9", "t9d1", "t9d2", "t9d3",
		"t10", "t10d1", "t10d2", "t10d3"));
    }

    public String httpRequest(String method,String targetUrl,String requestBodyJson) throws Exception {
		HttpURLConnection connection = null;
		StringBuffer sb = new StringBuffer("");
		
		try {
			URL url = new URL(targetUrl);
			connection = (HttpURLConnection) url.openConnection();

			connection.setDoOutput(true);
			connection.setDoInput(true);
			connection.setRequestMethod(method);// POST,GET,POST,DELETE,INPUT
			connection.setUseCaches(false);
			connection.setInstanceFollowRedirects(true);

			//connection.setRequestProperty("Content-Type", "application/json");
			connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
			//connection.setRequestProperty("Content-Type", "text/xml");  
			connection.setRequestProperty("Accept", "application/json");
			connection.setRequestProperty("Accept-Charset", "UTF-8");
			//connection.setRequestProperty("charset", "UTF-8");
			connection.connect();

			// OutputStream out = connection.getOutputStream();
			// out.write(requestBodyJson.getBytes());
			// out.flush();
			// out.close();
  
			BufferedReader reader = new BufferedReader(new InputStreamReader(
			connection.getInputStream(),"UTF-8"));
			
			String lines="";
			while ((lines = reader.readLine()) != null) {
				lines = new String(lines.getBytes(), "utf-8");
				sb.append( lines);
			}
			reader.close();
			connection.disconnect();
		} catch (Exception e) {  
			throw e;
		}
		return sb.toString();
	}

	public void LatencyTester() {
		try {
			for (int i = 0; i < testCounts.length; i++) {
				long sum = 0;
				String target = apiRequest + String.valueOf(seconds) + "/" + String.valueOf(testCounts[i]);
				Gson gson = new Gson();
				System.out.println("Testing: " + target);;
				for (int t = 0; t < testTimes; t++) {
					long t1 = System.currentTimeMillis();
					EcgRawData rawData = gson.fromJson(httpRequest("GET", target, target), EcgRawData.class);
					long t2 = System.currentTimeMillis();
					sum += (t2 - t1);
				}
				float avg = (float)sum / testTimes;
				testResults.put(testCounts[i], avg);
				// System.out.println("Latency: " + String.valueOf(testResults[i]));
				// System.out.println("PerPatient: " + String.valueOf(testResults[i] / testCounts[i]) + "\n");
			}
		} catch (Exception e) {  
			System.out.println("Spout exception: " + e);
		}
	}
 }
 