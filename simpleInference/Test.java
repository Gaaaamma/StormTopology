import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import com.google.gson.Gson;

// import org.json.JSONObject;

class Test {
    public static void main(String[] args) {
        try { 
			int seconds = 2;
            String target = "http://140.113.170.152:32777/users/ecg/rawdata/" + String.valueOf(seconds);
			Gson gson = new Gson();
			EcgRawData rawData = gson.fromJson(httpRequest("GET", target, target), EcgRawData.class);
			for (int i = 0; i < rawData.data.size(); i++) {
				System.out.println(rawData.data.get(i).Patient_CodeID);
				System.out.println(rawData.data.get(i).Ecg_time);
				System.out.println(rawData.data.get(i).Diff_1.size());
				System.out.println(rawData.data.get(i).Diff_2.size());
				System.out.println(rawData.data.get(i).Diff_3.size());
			}

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