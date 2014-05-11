import pickle
from nltk.classify import naivebayes, accuracy
from nltk.classify.util import LazyMap
from subprocess import Popen, PIPE, STDOUT

# Takes a string representation of a single discussion
# forum post and returns the bucket into which it was placed.
path_to_corenlp_jars = \
	'../lib/corenlp-python/stanford-corenlp-full-2013-11-12/*'
path_to_corenlp_sentiment = \
		'edu.stanford.nlp.sentiment.SentimentPipeline'

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

class PostClassifier:
	
	# Public Interface
	def classify_topic_unsupervised(self, post):
		# TODO: Implementation
		return 'education'
	def classify_topic_supervised(self, post):
		# TODO: Implementation
		return 'education'
	def classify_sentiment_train(self, path_to_labeled_data):
		# 1) Unpickle Data
		posts = unpickle_file(path_to_labeled_data)

		# 2) Eliminate Noise Words and Inflate sentiment_feature_words
		self.sentiment_features = self.build_sentiment_features(posts)

		# Build the training set	
		training_set = self.lazy_apply_feautres(posts)

		# 4) Train Classifier
		self.sentiment_classifier = \
			naivebayes.NaiveBayesClassifier.train(training_set)	
	def classify_sentiment_test(self, path_to_testing_data):
		# TODO: Take two -- NLTK Classification
		# 1) Unpickle data
		posts = unpickle_file(path_to_testing_data)
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
		# 4) Print accuracy / recall / precision / etc.
		return (test_accuracy, errors)

	def classify_sentiment(self, sentence):
		features = self.extract_features(sentence.split())
		return self.sentiment_classifier.classify(features)

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
