package source.utils;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DBConnection {

  public String driver;
  public String user;
  public String password;
  public String url;
  public String dbSchema;
  public String jobId;
  public String jobType;
  Connection conn = null;

  public DBConnection(String driver, String url, String user, String password, String dbSchema) {
    this.driver = driver;
    this.url = url;
    this.user = user;
    this.password = password;
    this.dbSchema = dbSchema;
  }

  public Connection connect() {
    try {
      if (conn != null && !conn.isClosed()) {
        return conn;
      }
    } catch (SQLException e1) {
      System.err.println(e1.getMessage());
      throw new RuntimeException("Connection while checking connection state");
    }
    try {
      Class.forName(driver);
    } catch (ClassNotFoundException e) {
      System.err.println(e.getMessage());
      throw new RuntimeException("Could not load driver " + driver);
    }
    try {
      conn = DriverManager.getConnection(url, user, password);
    } catch (SQLException e) {
      System.err.println(e.getMessage());
      throw new RuntimeException("Could not get database connection " + url);
    }

    return conn;
  }

  public void close() {
    try {
      if (conn != null) {
        conn.close();
      }
    } catch (SQLException e) {
      System.err.println(e.getMessage());
    }
  }



}
