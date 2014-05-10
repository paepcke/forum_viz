from forum import Forum, Format
from classify import PostClassifier
import argparse

host = 'datastage.stanford.edu'
db = 'EdxForum'
table = 'contents'
default_course_name = 'Medicine/HRP258/Statistics_in_Medicine'
attr = ['user_int_id', 'body']

def retrieve_posts(user, course):
	forum = Forum(user=user, host=host, db=db)
	return forum.post_contents(attr, table, course)

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
		output = '---POST---' + '\nauthor id: ' + str(entry.user_int_id) + \
			'\nclass: ' + entry.label + '\nsentences and sentiments:\n' + \
				'\n'.join(' : '.join(pair) for pair in entry.sentences)
		if (f is not None):
			f.write(output)
		else:
			print output
	
def main():
	parser = argparse.ArgumentParser(description='Uses classify module ' \
		'to fetch, classify, and dump posts.')
	parser.add_argument('-u', '--username', type=str,
		help='username for database')
	parser.add_argument('-cn', '--coursename', type=str,
		help='Retrieve posts for a particular course; course defaults to ' \
			+ default_course_name)
	args = parser.parse_args()

	user = args.username if args.username is not None else ''
	course = args.course if args.coursename is not None else default_course_name
	posts = retrieve_posts(user, course)
	classify_and_write_results(posts)

if __name__ == "__main__":
    main()
