from forum import Forum, Format
from classify import PostClassifier
import getpass

host = 'datastage.stanford.edu'
user = 'akshayka'
db = 'EdxPrivate'
table = 'ForumRaw'
default_course_name = 'Medicine/HRP258/Statistics_in_Medicine'

def retrieve_posts():
	# Get information needed to establish connection to database
	password = getpass.getpass("Password: ")
	course_name = raw_input(
		'Course name (empty defaults to ' + default_course_name + '): ')
	if (len(course_name) == 0):
		course_name = default_course_name 

	# Fetch posts
	forum = Forum(host, user, password, db)
	return forum.post_contents(table, course_name, ['author_id', 'body'])

def classify_and_write_results(posts):
	formatter = Format()
	classifier = PostClassifier()
	output_file = raw_input("Output file (empty defaults to stdout): ")
	try:
		f = open(output_file, 'w')
	except IOError:
		print 'Invalid filename entered. Printing dumped content ... '
		f = None
	for entry in posts:
		entry.sentences = formatter.split_sentences(entry.body)
		entry.sentences = zip(
			entry.sentences, classifier.classify_sentiment(entry.sentences))
		entry.label = classifier.classify_topic_unsupervised(entry.body)
		output = '---POST---' + '\nauthor: ' + str(entry.author_id) + \
			'\nclass: ' + entry.label + '\nsentences and sentiments:\n' + \
				'\n'.join(' : '.join(pair) for pair in entry.sentences)
		if (f is not None):
			f.write(output)
		else:
			print output
	
def main():
	posts = retrieve_posts()
	classify_and_write_results(posts)

if __name__ == "__main__":
    main()
