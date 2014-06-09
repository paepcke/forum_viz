from classify import PostClassifier

train_path = raw_input("Path to training data: ")
classifier = PostClassifier()
classifier.classify_sentiment_train(train_path)

while True:
	sentence = raw_input("Sentence to classify: ")
	print "Guess: " + classifier.classify_sentiment(sentence)	
