'''

A simple tool that fetches posts from a specified course that
have emoticons in them. Allows clients to either print or
pickle the fetched posts.

@author Akshay Agrawal: akshayka@cs.stanford.edu
'''
from forum import Forum
import util

import argparse
import pickle
from random import shuffle

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
test_percent = 0.4

def generate_data(forum, course, path, pos_ratio_arg, runs, verbose):
	course_list	= []
	if course is None:
		course_list = forum.course_names()
	else:
		course_list = [course]
	for run in range (1, runs + 1):
		if verbose:
			print 'Run number ' + str(run)
		all_pos_posts = []
		all_neg_posts = []
		for course in course_list:
			if verbose:
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

		# Add labels to the classified data
		for index, item in enumerate(all_pos_posts):
			item.forum_viz_label = 'positive'
			all_pos_posts[index] = item
		for index, item in enumerate(all_neg_posts):
			item.forum_viz_label = 'negative'
			all_neg_posts[index] = item

		# Generate the training and test data
		shuffle(all_pos_posts)
		shuffle(all_neg_posts)
		total_num_posts = len(all_pos_posts) + len(all_neg_posts)

		pos_ratio = float(len(all_pos_posts)) / total_num_posts
		neg_ratio = 1 - pos_ratio

		if pos_ratio_arg is not None:
			# Artificially deflate the number of positive posts or the number of
			# negative posts, if pos_ratio_arg does not equal pos_ratio.
			if pos_ratio_arg > pos_ratio:
				total_num_posts = int(float(len(all_pos_posts)) / pos_ratio_arg)
				reduced_neg_posts = total_num_posts - len(all_pos_posts)
				all_neg_posts = all_neg_posts[:reduced_neg_posts]
			elif 1 - pos_ratio_arg > neg_ratio:
				total_num_posts = int(float(len(all_neg_posts)) / (1 - pos_ratio_arg))
				reduced_pos_posts = total_num_posts - len(all_neg_posts)
				all_pos_posts = all_pos_posts[:reduced_pos_posts]
				pos_ratio = pos_ratio_arg
				neg_ratio = 1 - pos_ratio
					
		train_pos_num = int(train_percent * total_num_posts * pos_ratio)
		train_neg_num = int(train_percent * total_num_posts * neg_ratio)
		test_pos_num = len(all_pos_posts) - train_pos_num
		test_neg_num = len(all_neg_posts) - train_neg_num

		try:
			f_train = open(path + str(run) + '_train_sample_pos_' + \
			str(train_pos_num) + '_neg_' + str(train_neg_num), 'wb')
			f_test = open(path + str(run) + '_test_sample_pos_' + \
			str(test_pos_num) + '_neg_' + str(test_neg_num), 'wb')
		except IOError:
			print 'failed to open train / test'
			return

		util.pickle_posts_to_file(f_train, all_pos_posts[:train_pos_num])
		util.pickle_posts_to_file(f_train, all_neg_posts[:train_neg_num])

		util.pickle_posts_to_file(f_test, all_pos_posts[train_pos_num:])
		util.pickle_posts_to_file(f_test, all_neg_posts[train_neg_num:])

		f_train.close()
		f_test.close()
			
def main():
	# Args: username [optional] (course name [optional], emotion [optional]) or (path [optional])
	parser = argparse.ArgumentParser(description='Simple tool to fetch ' \
		'posts with emoticons. Includes options to simply print the data, '\
			'or to dump it as pickled files.')
	parser.add_argument('-u', '--username', type=str,
		help='username for database')
	parser.add_argument('-cn', '--coursename', type=str,
		help='Retrieve posts for a particular course; defaults to all courses')
	parser.add_argument('-p', '--path', type=str, default='./',
		help='Directory to write the training and testing data to; defaults to ' \
			'the working directory.')
	parser.add_argument('-pr', '--positive_ratio', type=float,
		help='Percentage of positive labeled posts to collect; defaults to \
        	a representative proportion.')
	parser.add_argument('-r', '--runs', type=int, default=1,
		help='Number of pairs of training data to produce')
	parser.add_argument ('-v', '--verbose', default=False, action='store_true',
		help='verbose')
	args = parser.parse_args()

	user = args.username if args.username is not None else ''
	forum = Forum(user=user, host=host, db=db)

	if not args.path.endswith('/'):
		args.path = args.path + '/'
	assert args.runs > 0, 'Runs must be at least 1'
	generate_data(forum, args.coursename, args.path, args.positive_ratio, \
		args.runs, args.verbose)

if __name__ == "__main__":
	main()
