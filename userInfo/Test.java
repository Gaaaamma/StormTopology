import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Iterator;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

// import org.json.JSONObject;

class Test {
    public static void main(String[] args) {
        Integer index = 0;
        try { 
            String[] patientID = {"NCTU0000", "NCTU0001", "NCTU0002"};
            String target = "http://140.113.170.152:32777/users/" + patientID[index % 3];
            index += 1;

			JsonObject jsonObject = new JsonParser().parse(httpRequest("GET", target, target)).getAsJsonObject();
			System.out.println(jsonObject.get("userId").getAsString());
			System.out.println(jsonObject.get("lasttime_12lead"));
			System.out.println(jsonObject.get("subStartTime").getClass());

			Iterator<JsonElement> iterator = jsonObject.get("subStartTime").getAsJsonArray().iterator();
        	while (iterator.hasNext()) {
        	    JsonElement element = iterator.next();
        	    int value = element.getAsInt();
        	    System.out.println(value);
        	}
        } catch (Exception e) {

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