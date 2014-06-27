from classify import PostClassifier

train_path = raw_input("Path to training data: ")
lower_threshold = int(raw_input("Lower threshold: "))
negative_bucket  = raw_input("Use negative bucket feature? (True/False): ") == "True"

classifier = PostClassifier()
classifier.sentiment_train(train_path, lower_threshold, negative_bucket)
while True:
	sentence = raw_input("Sentence to classify: ")
	print "Guess: " + classifier.classify_sentiment(sentence)	
