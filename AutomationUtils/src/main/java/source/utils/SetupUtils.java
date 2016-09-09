package source.utils;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.apache.commons.lang3.StringUtils;

public class SetupUtils {

  public static Properties getProperties(String config) {
    InputStream inputStream = null;
    try {

      Properties prop = new Properties();
      String propFileName = config;

      inputStream = new FileInputStream(new File(propFileName));
      prop.load(inputStream);
      return prop;
    } catch (FileNotFoundException e) {
      throw new RuntimeException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    } finally {
      if (inputStream != null) {
        try {
          inputStream.close();
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
      }
    }
  }

  public static String getNonNull(Properties properties, String name) {
    String val = properties.getProperty(name);
    if (StringUtils.isEmpty(val)) {
      throw new RuntimeException("property " + name + " not specified.");
    }
    return val;
  }


}
