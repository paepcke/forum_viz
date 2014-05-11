import argparse
from forum import Forum
import pickle

host = 'datastage.stanford.edu'
db = 'EdxForum'
default_course_name = 'Medicine/HRP258/Statistics_in_Medicine'
table = 'contents'
attr = ['body']
			
fields = ','.join(attr)
happy_emoticons = '.*(:-?|=|;)[])DP].*'
sad_emoticons = '.*(:-?|=)[[(].*'
all_emoticons = '.*(:-?|=|;)[])DP[(].*'

def write_posts_to_file(f, posts, label):
	for post in posts:
		words  = [w.lower() for w in post.body.split()]
		entry = (words, label)
		pickle.dump(entry, f)

def write_all_training(forum, path):
	courses = forum.course_names()
	for course in courses:
		print 'Fetching posts for course ' + course
		pos_posts = forum.post_contents(attr, \
			query='select ' + fields + ' from ' + table + \
				' where course_display_name="' + course + '" AND '\
					'body rlike "' + happy_emoticons + '"')
		neg_posts = forum.post_contents(attr, \
			query='select ' + fields + ' from ' + table + \
				' where course_display_name="' + course + '" AND '\
					'body rlike "' + sad_emoticons + '"')
		pos_len = len(pos_posts)
		neg_len = len(neg_posts)
		upper_bound = pos_len if pos_len < neg_len else neg_len
		if (pos_len + neg_len > 0):
			course = course.replace('/', '_')
			try:
				f_pos = open(path + 'positive/' + course + '_' + \
					str(pos_len) + '_pos', 'wb')
				f_neg = open(path + 'negative/' + course + '_' + \
					str(neg_len) + '_neg', 'wb')
				f_all = open(path + 'all/' + course + '_' + \
					str(pos_len + neg_len) + '_all', 'wb')	
				f_balance = open(path + 'balance/' + course + '_' + \
					str(upper_bound) + '_bal', 'wb')	
			except IOError:
				print 'failed to open file for course ' + course
				return
			print 'Writing posts for course ' + course
			write_posts_to_file(f_pos, pos_posts, "positive")
			write_posts_to_file(f_all, pos_posts, "positive")
			write_posts_to_file(f_neg, neg_posts, "negative")
			write_posts_to_file(f_all, neg_posts, "negative")

			write_posts_to_file(f_balance, pos_posts[:upper_bound], "positive")
			write_posts_to_file(f_balance, neg_posts[:upper_bound], "negative")

			f_pos.close()
			f_neg.close()
			f_all.close()
			f_balance.close()
			
def print_course_emoticons(forum, course_name, regex):
	emoticon_posts = forum.post_contents(attr,
		query='select ' + fields + ' from ' + table + \
			' where course_display_name="' + course_name + '" AND '\
				'body rlike "' + regex + '"')

	count = 0
	for post in emoticon_posts:
		print str(count) + ':<' + post.body + '>'
		count += 1

def main():
	# Args: username [optional] (course name [optional], emotion [optional]) or (path [optional])
	parser = argparse.ArgumentParser(description='Simple tool to fetch ' \
		'posts with emoticons. Includes options to simply print the data, '\
			'or to dump it as pickled files.')
	parser.add_argument('-u', '--username', type=str,
		help='username for database')
	parser.add_argument('-cn', '--coursename', type=str,
		help='Retrieve posts for a particular course; course defaults to ' \
			+ default_course_name)
	parser.add_argument('-em', '--emotion', type=str,
		help='Retrieve posts matching a particular emoticon type: ' \
			'one of \'happy\', \'sad\', or \'all\'; defaults to \'all\'.')
	parser.add_argument('-p', '--path', type=str,
		help='For every course, fetch all posts containing an emoticon ' \
			'and write them to files specificed directory. The supplied ' \
				'directory must have subdirectories \'positive\', \'negative\'.')
	args = parser.parse_args()

	user = args.username if args.username is not None else ''
	forum = Forum(user=user, host=host, db=db)
	if args.path is not None:
		if not args.path.endswith('/'):
			args.path = args.path.append('/')
		write_all_training(forum, args.path)
	else:
		if args.coursename is None:
			course_name = default_course_name
		else:
			course_name = args.coursename

		if args.emotion is None:
			regex = all_emoticons
		elif args.emotion == 'happy':
			regex = happy_emoticons
		elif args.emotion == 'sad':
			regex = sad_emoticons
		else:
			regex = all_emoticons
		
		print_course_emoticons(forum, course_name, regex)

if __name__ == "__main__":
	main()
