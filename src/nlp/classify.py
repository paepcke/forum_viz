from subprocess import Popen, PIPE, STDOUT

# Takes a string representation of a single discussion
# forum post and returns the bucket into which it was placed.
path_to_corenlp_jars = \
	'../lib/corenlp-python/stanford-corenlp-full-2013-11-12/*'
path_to_corenlp_sentiment = \
		'edu.stanford.nlp.sentiment.SentimentPipeline'

class PostClassifier:
	def classify_topic_unsupervised(self, post):
		# TODO: Implementation
		return 'education'
	def classify_topic_supervised(self, post):
		# TODO: Implementation
		return 'education'
	def classify_sentiment(self, sentences):
		# A basic implementation that uses the stanford sentiment classifier
		args = ['java', '-cp', path_to_corenlp_jars, \
			'-mx5g', path_to_corenlp_sentiment, '-stdin']
		p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
		sentiment_str = p.communicate(input='\n'.join(sentences))[0]
		sentiment_list = sentiment_str.split('\n')[8:]
		return [sentiment.strip() for sentiment in sentiment_list]
