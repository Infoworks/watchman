from tasks import infoworks

def main():
	"""
	Main Driver
	Creates a source based on the configuration
	"""
	print "hello!"

	infoworks.create_source('a', 'b')
	infoworks.crawl_metadata('s')

main()