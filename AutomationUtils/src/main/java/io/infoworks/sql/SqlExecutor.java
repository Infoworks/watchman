package io.infoworks.sql;

import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.util.logging.Logger;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;

import source.utils.Constants;
import source.utils.DBConnection;
import source.utils.SetupUtils;

public class SqlExecutor {

	private static String dbConfFilePath;
	private static String sqlCommand;
	private static PrintWriter logWriter = new PrintWriter(System.out);
	private static PrintWriter errorLogWriter = new PrintWriter(System.err);

	private static Logger logger = Logger.getLogger("SqlExecutor");

	public static void main(String[] args) {
		
		try {
			parseOptions(args);
			DBConnection db = SetupUtils.getDBConnection(dbConfFilePath) ;
			Connection conn = db.connect() ;
			ResultSet result = conn.createStatement().executeQuery(sqlCommand) ;
			while(result.next()) {
				//result.getMetaData().
				long count = result.getLong(1);
				logger.info("result :" + count);
				logWriter.println("" + count);
			}
			
			System.exit(0);
		}
		catch(Exception e) {
			logger.severe("exception occurred while executing sql:" + e.getMessage());
			errorLogWriter.println("exception occurred while executing sql:" + e.getMessage());
			e.printStackTrace(); 
			System.exit(-1);
		}
	}

	@SuppressWarnings("static-access")
	private static void parseOptions(String[] args) {
		CommandLine commandLine;
		Option option1 = OptionBuilder.withArgName("DBConfFile").hasArg().withDescription("DB conf file path")
				.create(Constants.CONF_FILE);
		Option option2 = OptionBuilder.withArgName("sql").hasArg().withDescription("sql to be executed")
				.create(Constants.SQL_COMMAND);
		Options options = new Options();
		CommandLineParser parser = new GnuParser();

		options.addOption(option1);
		options.addOption(option2);

		try {
			commandLine = parser.parse(options, args);

			if (commandLine.hasOption(Constants.CONF_FILE)) {
				dbConfFilePath = commandLine.getOptionValue(Constants.CONF_FILE);
			} else {
				throw new RuntimeException(Constants.CONF_FILE + " option is not set");
			}

			if (commandLine.hasOption(Constants.SQL_COMMAND)) {
				sqlCommand = commandLine.getOptionValue(Constants.SQL_COMMAND);
			} else {
				throw new RuntimeException(Constants.SQL_COMMAND + " sql command is not passed");
			}
		} catch (Exception e) {
			e.printStackTrace();
			logger.severe("Errow while parsing options " + e.getMessage());
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("AutomationUtils.jar", options);
		}

	}

	
}
