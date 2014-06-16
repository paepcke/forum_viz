'''

A simple tool that fetches posts from a specified course that
have emoticons in them. Allows clients to either print or
pickle the fetched posts.

@author Akshay Agrawal: akshayka@cs.stanford.edu
'''

import argparse
from forum import Forum
import pickle
from random import shuffle
import re

host = 'datastage.stanford.edu'
db = 'EdxForum'
default_course_name = 'Medicine/HRP258/Statistics_in_Medicine'
table = 'contents'
attr = ['body']
			
fields = ','.join(attr)
happy_emoticons = '.*(:-?|=|;)[])DP].*'
sad_emoticons = '.*(:-?|=)[[(].*'
all_emoticons = '.*(:-?|=-?|;-?)[])DP[(].*'

token_regex = '[\w+\']|(' + all_emoticons + ')|[.,!?;]'

train_percent = 0.6
dev_percent = 0.2
test_percent = 0.2

def write_posts_to_file(f, posts, label):
	for post in posts:
		words = []
		for matches in re.findall(r"([\w']+)|((:-?|=-?|;-?)[]\)DP[\(])|([.,!?;])", post.body):
			found = list (matches)
			# TODO: This is a hack.
			# findall returns a list of four groups with the supplied regex. The third group
			# is irrelevant.
			found.pop(2)
			words.append (''.join(found).lower())
		entry = (words, label)
		pickle.dump(entry, f)

def write_all_training(forum, path, concise):
	courses = forum.course_names()
	all_pos_posts = []
	all_neg_posts = []
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
		all_pos_posts.extend(pos_posts)
		all_neg_posts.extend(neg_posts)
		pos_len = len(pos_posts)
		neg_len = len(neg_posts)
		if (pos_len + neg_len > 0 and not concise):
			upper_bound = pos_len if pos_len < neg_len else neg_len
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

	# Generate the training, dev, and test
	shuffle(all_pos_posts)
	shuffle(all_neg_posts)
	total_num_posts = len(all_pos_posts) + len(all_neg_posts)

	# TODO: It might be advisable to inflate the negative ratio
	#		and defalte the positive ratio.
	pos_ratio = float(len(all_pos_posts)) / total_num_posts
	neg_ratio = 1 - pos_ratio

	train_pos_num = int(train_percent * total_num_posts * pos_ratio)
	train_neg_num = int(train_percent * total_num_posts * neg_ratio)
	dev_pos_num = int(dev_percent * total_num_posts * pos_ratio)
	dev_neg_num = int(dev_percent * total_num_posts * neg_ratio)
	test_pos_num = len(all_pos_posts) - (train_pos_num + dev_pos_num)
	test_neg_num = len(all_neg_posts) - (train_neg_num + dev_neg_num)

	try:
		f_train = open(path + 'train_sample_pos_' + \
			str(train_pos_num) + '_neg_' + str(train_neg_num), 'wb')
		f_dev = open(path + 'dev_sample_pos_' + \
			str(dev_pos_num) + '_neg_' + str(dev_neg_num), 'wb')
		f_test = open(path + 'test_sample_pos_' + \
			str(test_pos_num) + '_neg_' + str(test_neg_num), 'wb')
	except IOError:
		print 'failed to open train / dev / test'
		return

	write_posts_to_file(f_train, all_pos_posts[:train_pos_num], 'positive')
	write_posts_to_file(f_train, all_neg_posts[:train_neg_num], 'negative')

	write_posts_to_file(f_dev,
		all_pos_posts[train_pos_num:train_pos_num + dev_pos_num], 'positive')
	write_posts_to_file(f_dev,
		all_neg_posts[train_neg_num:train_neg_num + dev_neg_num], 'negative')

	write_posts_to_file(f_test, all_pos_posts[train_pos_num + dev_pos_num:], 'positive')
	write_posts_to_file(f_test, all_neg_posts[train_neg_num + dev_neg_num:], 'negative')

	f_train.close()
	f_dev.close()
	f_test.close()
			
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
	parser.add_argument('-c', '--concise', default=False, action='store_true',
		help='If included, only generate three files: ' \
			'training data, dev data, and test data.')
	args = parser.parse_args()

	user = args.username if args.username is not None else ''
	forum = Forum(user=user, host=host, db=db)
	if args.path is not None:
		if not args.path.endswith('/'):
			args.path = args.path + '/'
		write_all_training(forum, args.path, args.concise)
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
