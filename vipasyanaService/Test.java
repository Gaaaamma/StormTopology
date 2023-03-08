import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import com.google.gson.Gson;

// import org.json.JSONObject;

class Test {
    public static void main(String[] args) {
        try { 
			int seconds = 10;
            String target = "http://140.113.170.152:32777/users/ecg/rawdata/" + String.valueOf(seconds);
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
						System.out.println("A: ");
						System.out.println(patient);
						for (int j = 0; j < diff1.size(); j++) {
							System.out.println(timestamps[j]);
						}
						System.out.println(diff1.size() + " : " + diff2.size() + " : " + diff3.size());
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
				System.out.println("B: ");
				System.out.println(patient);
				for (int j = 0; j < diff1.size(); j++) {
					System.out.println(timestamps[j]);
				}				
				System.out.println(diff1.size() + " : " + diff2.size() + " : " + diff3.size());
			}

			// Values v = new Values(patientId, dataLength, t1, t1d1, t1d2, t1d3, t2, ...);

        } catch (Exception e) {
			System.out.println("Spout exception: " + e);
        }
    }
    public static String httpRequest(String method,String targetUrl,String requestBodyJson) throws Exception {
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
}