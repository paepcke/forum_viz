from nltk.classify import naivebayes, accuracy
from nltk.classify.util import LazyMap
from nltk.corpus import stopwords
from subprocess import Popen, PIPE, STDOUT
import operator
import util

path_to_corenlp_jars = \
	'../lib/corenlp-python/stanford-corenlp-full-2013-11-12/*'
path_to_corenlp_sentiment = \
	'edu.stanford.nlp.sentiment.SentimentPipeline'
stop_words = stopwords.words('english')

class PostClassifier:
	
	def classify_topic_unsupervised(self, post):
		# TODO: Implementation
		return 'education'
	def classify_topic_supervised(self, post):
		# TODO: Implementation
		return 'education'

	'''
	Classify a single post by sentiment.

	@precondition classify_sentiment_train must be invoked before calling
				  this method.
	@return The label guessed for this post.
	'''
	def classify_sentiment(self, post):
		features = self.sentiment_extract_features(post.split())
		return self.sentiment_classifier.classify(features)


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
	def sentiment_train(self, path_to_labeled_data):
		# 1) Unpickle data
		posts = util.unpickle_file(path_to_labeled_data)

		# 2) Eliminate noise words and inflate sentiment_features
		self.sentiment_features = self.build_sentiment_features(posts)

		# Build the training set	
		training_set = self.lazy_apply_feautres(posts)

		# 4) Train Classifier
		self.sentiment_classifier = \
			naivebayes.NaiveBayesClassifier.train(training_set)	
		self.sentiment_classifier.show_most_informative_features(300)

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
	def sentiment_test(self, path_to_testing_data):
		# 1) Unpickle data
		posts = util.unpickle_file(path_to_testing_data)

		# 2) Extract features
		testing_set = self.lazy_apply_feautres(posts)

		# 3) Test with classifier
		print 'Testing ...'
		errors = []
		f_iter  = testing_set.iterate_from(0)
		false_pos = false_neg = 0
		for (post, sentiment) in posts:
			features = f_iter.next()[0]
			guess = self.sentiment_classifier.classify(features)
			if guess != sentiment:
				errors.append((guess, sentiment, post))
				if guess == 'positive':
					false_pos += 1
				else:
					false_neg += 1
		# TODO Clean this up
		print "fp: " + str (false_pos)
		print "fn: " + str (false_neg)
		return (len (errors) / len (posts), errors)

	def classify_sentiment_core_nlp(self, sentences):
		# A basic implementation that uses the stanford sentiment classifier
		args = ['java', '-cp', path_to_corenlp_jars, \
			'-mx5g', path_to_corenlp_sentiment, '-stdin']
		p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
		sentiment_str = p.communicate(input='\n'.join(sentences))[0]
		sentiment_list = sentiment_str.split('\n')[8:]
		return [sentiment.strip() for sentiment in sentiment_list]

	def sentiment_extract_features(self, post):
		post_set = set(post)
		features = {}
		for feature in self.sentiment_features:
			features['contains(%s)' % feature] = (feature in post_set)
		return features
			
	def lazy_apply_feautres(self, toks):
		def lazy_func(labeled_token):
			return (self.sentiment_extract_features(
				labeled_token[0]), labeled_token[1])
		return LazyMap(lazy_func, toks)

	@staticmethod
	# TODO: I want a more fine-grained feature set.
	# Perhaps filter out the more common words as well?
	# Perhaps come up with an ad-hoc list of words that
	# shouldn't be filtered out as well?
	# Ideas:
	# tf-idf
	# just chuck out words that don't seem meaningful
	# bigrams / trigrams
	# probably going to have to implement my own naive bayes
	# 	variant so that I can try tf-idf
	def build_sentiment_features(posts):
		# calculate frequencies
		freqmap = {}
		for (words, sentiment) in posts:
			for w in [x for x in words if x not in stop_words]:
				if w in freqmap:
					freqmap[w] += 1
				else:
					freqmap[w] = 1	
		sorted_freq = sorted (freqmap.iteritems(), key=operator.itemgetter(1))
		features = []
		for (key, value) in sorted_freq:
			# Filter out uncommon / esoteric words
			if value >= 20: #TODO This feels hacky as well & the number seems too high
				features.append(key)
		return set(features)
