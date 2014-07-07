'''
A collection of convenience tools related to
the classification task.

@author: Akshay Agrawal
May 10, 2014
'''
import pickle
import re

'''
Given a path to a file containing pickled objects,
open said file and unpickle the objects, storing each
within an array.

@param path_to_file: The path to the file with pickled data.
@type path_to_file: string
@return A list of the unpickled objects in the order in which
		they appear in the file; returns on error.
'''
def unpickle_file(path_to_file):
	# Open the file for unpickling.
	try:
		f = open(path_to_file, 'rb')
	except IOError:
		return None
	# Unpickle each entry in the file and inflate our list
	posts = []
	while True:
		try:
			posts.extend(pickle.load(f))
		except EOFError:
			break
	return posts

# NB: Each post must have a "forum_viz_label"
def pickle_posts_to_file(f, posts):
	pickle_objects = []
	for post in posts:
		words = []
		for matches in re.findall(r"([\w']+)|((:-?|=-?|;-?)[]\)DP[\(])|([.,!?;])", post.body):
			found = list (matches)
			# TODO: This is a hack.
			# findall returns a list of four groups with the supplied regex. The third group
			# is irrelevant.
			found.pop(2)
			words.append (''.join(found).lower())
		entry = (words, post.forum_viz_label)
		pickle_objects.append(entry)
	if len(pickle_objects) > 0:
		pickle.dump(pickle_objects, f)

def is_number(num_str):
	try:
		float(num_str)
		return True
	except ValueError:
		return False
