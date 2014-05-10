import argparse
from forum import Forum
import pickle

default_course_name = 'Medicine/HRP258/Statistics_in_Medicine'
table = 'contents'
attr = ['body']
			
fields = ','.join(attr)
happy_emoticons = '.*(:-?|=|;)[])DP].*'
sad_emoticons = '.*(:-?|=)[[(].*'
all_emoticons = '.*(:-?|=|;)[])DP[(].*'

#TODO: Pickle the training data s.t. we have a dataset
# that can be easily manipulated.
#
# Idea: (features_list, emoticon)
# Do not make any decisions here about which features
# to remove, etc. Dump them all.
def write_posts_to_file(f, posts, label):
	count = 0
	for post in posts:
		words  = [w.lower() for w in post.body.split()]
		entry = (words, label)
		pickle.dump(entry, f)

def write_all_training(forum, path):
	# Get list of all course names
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
		if (pos_len + neg_len > 0):
			course = course.replace('/', '_')
			try:
				f_pos = open(path + 'positive/' + course + '_' + \
					str(pos_len) + '_pos_tr', 'wb')
				f_neg = open(path + 'negative/' + course + '_' + \
					str(neg_len) + '_neg_tr', 'wb')
			except IOError:
				print 'failed to open file for course ' + course
				return
			print 'Writing posts for course ' + course
			write_posts_to_file(f_pos, pos_posts, "positive")
			write_posts_to_file(f_neg, neg_posts, "negative")
			f_pos.close()
			f_neg.close()
			
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
	# Args: course name and emotion
	parser = argparse.ArgumentParser(description='Simple tool to fetch ' \
		'posts with emoticons.')
	parser.add_argument('-cn', '--coursename', type=str,
		help='name of course; defaults to' + default_course_name)
	parser.add_argument('-em', '--emotion', type=str,
		help='one of \'happy\', \'sad\', \'all\'; defaults to \'all\'.')
	parser.add_argument('-ac', '--allcourses', type=str,
		help='updates all training data, path to sentiment directory (include trailing /')
	args = parser.parse_args()

	forum = Forum()
	if args.allcourses is not None:
		write_all_training(forum, args.allcourses)
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
