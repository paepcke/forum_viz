'''
A collection of convenience tools related to
the classification task.

@author: Akshay Agrawal
May 10, 2014
'''
import pickle

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
			posts.append(pickle.load(f))
		except EOFError:
			break
	return posts
