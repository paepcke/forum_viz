from nltk.classify import naivebayes, accuracy
from nltk.classify.util import LazyMap
from subprocess import Popen, PIPE, STDOUT
import util

class PostClassifier:
	
	def classify_topic_unsupervised(self, post):
		# TODO: Implementation
		return 'education'
	def classify_topic_supervised(self, post):
		# TODO: Implementation
		return 'education'

	'''
	Given a path to a file containing word-label tuples for each post
	it describes, determines the space of features and trains a naive
	Bayes classifier accordingly. The file must contain pickled objects,
	each object a tuple
						(word list, sentiment),
	where 'word list' is a list of the words that appear in the post
	and 'sentiment' is a string describing the tone of the post. The
	trained classifier is stored in self.sentiment_classifier.

	@param path_to_labeled_data: The path to the labeled data file
	@type path_to_labeled_data: string
	'''
	def classify_sentiment_train(self, path_to_labeled_data):
		# 1) Unpickle Data
		posts = util.unpickle_file(path_to_labeled_data)

		# 2) Eliminate Noise Words and Inflate sentiment_feature_words
		self.sentiment_features = self.build_sentiment_features(posts)

		# Build the training set	
		training_set = self.lazy_apply_feautres(posts)

		# 4) Train Classifier
		self.sentiment_classifier = \
			naivebayes.NaiveBayesClassifier.train(training_set)	

	'''
	Given a path to a testing file (formatted in the same manner
	as the training data set -- see classify_sentiment_train),
	classifies the testing data and returns metrics describing
	its success (or lack thereof)
	
	@precondition classify_sentiment_train must be invoked
				  before calling this method.
	@param path_to_testing_data: The path to the testing file.
	@type path_to_testing_data: string
	@return A tuple (accuracy, errors), where accuracy is a double
			describing the success rate and errors is a list of three-tuples
			(guess, sentiment, post), where guess is the classification result,
			sentiment is the label attached to the post, and post is the text of
			the post (broken into words). A tuple appears in errors if and only
			if the guess did not match the sentiment.
	'''
	def classify_sentiment_test(self, path_to_testing_data):
		# 1) Unpickle data
		posts = util.unpickle_file(path_to_testing_data)
		# 2) Extract features
		testing_set = self.lazy_apply_feautres(posts)
		# 3) Test with classifier
		test_accuracy = accuracy(self.sentiment_classifier, testing_set)
		errors = []
		f_iter  = testing_set.iterate_from(0)
		i = 0
		for (post, sentiment) in posts:
			features = f_iter.next()[0]
			guess = self.sentiment_classifier.classify(features)
			if guess != sentiment:
				errors.append((guess, sentiment, post))
		return (test_accuracy, errors)

	'''
	Classify a single post by sentiment.

	@precondition classify_sentiment_train must be invoked before calling
				  this method.
	@return The label guessed for this post.
	'''
	def classify_sentiment(self, post):
		features = self.extract_features(post.split())
		return self.sentiment_classifier.classify(features)

	path_to_corenlp_jars = \
		'../lib/corenlp-python/stanford-corenlp-full-2013-11-12/*'
	path_to_corenlp_sentiment = \
		'edu.stanford.nlp.sentiment.SentimentPipeline'

	def classify_sentiment_core_nlp(self, sentences):
		# A basic implementation that uses the stanford sentiment classifier
		args = ['java', '-cp', path_to_corenlp_jars, \
			'-mx5g', path_to_corenlp_sentiment, '-stdin']
		p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
		sentiment_str = p.communicate(input='\n'.join(sentences))[0]
		sentiment_list = sentiment_str.split('\n')[8:]
		return [sentiment.strip() for sentiment in sentiment_list]

	def extract_features(self, post):
		post_set = set(post)
		features = {}
		for word in self.sentiment_features:
			features['contains(%s)' % word] = (word in post_set)
		return features
			
	def lazy_apply_feautres(self, toks):
		def lazy_func(labeled_token):
			return (self.extract_features(labeled_token[0]), labeled_token[1])
		return LazyMap(lazy_func, toks)

	#TODO Filter out stop words 
	@staticmethod
	def build_sentiment_features(posts):
		features = []
		for (words, sentiment) in posts:
			features.extend(words)
		return features	
