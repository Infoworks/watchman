package source.setup;

import java.io.FileReader;
import java.io.Reader;
import java.sql.Connection;
import java.util.Properties;
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
import source.utils.ScriptRunner;
import source.utils.SetupUtils;

public final class SourceSetup {
	private static String dbConfFilePath;
	private static String scriptPath;

	public static void main(String[] args) {
		Connection con = null;
		DBConnection db = null;
		try {
			parseOptions(args);
			Properties properties = SetupUtils.getProperties(dbConfFilePath);
			db = new DBConnection(SetupUtils.getNonNull(properties, Constants.JDBC_DRIVER),
					SetupUtils.getNonNull(properties, Constants.JDBC_URL),
					SetupUtils.getNonNull(properties, Constants.USERNAME),
					SetupUtils.getNonNull(properties, Constants.PASSWORD),
					SetupUtils.getNonNull(properties, Constants.DB_SCHMEA));
			con = db.connect();
			if (con != null) {
				System.out.println("Connection established succesfully");
			}
			Reader fileReader = new FileReader(scriptPath);
			ScriptRunner sc = new ScriptRunner(con, false, false);
			sc.runScript(fileReader);
			db.close();
			System.exit(0);
		} catch (Exception e) {
			e.printStackTrace();
			System.err.println("Error occurred: " + e.getMessage());
			System.exit(-1);
		} finally {
			if (con != null) {
				db.close();
			}
		}
	}

	@SuppressWarnings("static-access")
	private static void parseOptions(String[] args) {
		CommandLine commandLine;
		Option option1 = OptionBuilder.withArgName("DBConfFile").hasArg().withDescription("DB conf file path")
				.create(Constants.CONF_FILE);
		Option option2 = OptionBuilder.withArgName("SqlScript").hasArg().withDescription("script file path")
				.create(Constants.SCRIPT_FILE);
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

			if (commandLine.hasOption(Constants.SCRIPT_FILE)) {
				scriptPath = commandLine.getOptionValue(Constants.SCRIPT_FILE);
			} else {
				throw new RuntimeException(Constants.SCRIPT_FILE + " option is not set");
			}
		} catch (Exception e) {
			e.printStackTrace();
			System.err.println("Errow while parsing options " + e.getMessage());
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("AutomationUtils.jar", options);
		}

	}
}
