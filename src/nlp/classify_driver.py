from forum import Forum
from classify import PostClassifier
import getpass

host = 'datastage.stanford.edu'
user = 'akshayka'
db = 'EdxPrivate'
table = 'ForumRaw'


def main():
	password = getpass.getpass("Password: ")
	# Note: A working course name is 'Medicine/HRP258/Statistics_in_Medicine'
	course_name = raw_input("Course name: ")	
	output_file = raw_input("Output file: ")
	forum = Forum(host, user, password, db)
	posts = forum.post_contents(table, course_name, ['author_id', 'body'])

	classifier = PostClassifier()
	try:
		f = open(output_file, 'w')
	except IOError:
		print 'Invalid filename entered. Printing dumped content ... '
		f = None

	for entry in posts:
		entry.label = classifier.classify(entry.body)
		output = '---POST---' + '\n author: ' + str(entry.author_id) + \
			'\n class: ' + entry.label + '\n body: ' + entry.body + '\n'
		if (f is not None):
			f.write(output)
		else:
			print output

if __name__ == "__main__":
    main()
