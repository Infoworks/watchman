package java.io.infoworks.sql;

import source.setup.CommandLine;
import source.setup.CommandLineParser;
import source.setup.GnuParser;
import source.setup.HelpFormatter;
import source.setup.Option;
import source.setup.Options;
import source.utils.Constants;

public class SqlExecutor {
	private String dbConfFilePath ;
	private String strSql ;
	
	public static void main(String[] args) {
		
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
			logger.severe("Errow while parsing options " + e.getMessage());
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("AutomationUtils.jar", options);
		}

	}
}
