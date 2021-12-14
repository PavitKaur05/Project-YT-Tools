import lxml
import requests
import time
import sys
# import progress_bar as PB


def progress(count, total, cond=False):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    if cond == False:
    	sys.stdout.write('[%s] %s%s\r' % (bar, percents, '%'))
    	sys.stdout.flush()

    else:
    	sys.stdout.write('[%s] %s%s' % (bar, percents, '%'))
     

YOUTUBE_IN_LINK = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=100&order=relevance&pageToken={pageToken}&videoId={videoId}&key={key}'
YOUTUBE_LINK = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=100&order=relevance&videoId={videoId}&key={key}'
key = 'AIzaSyCEtAL1s9JyCVlDGoae11_F9K9js0E8WRg'
	
def commentExtract(videoId, count = -1):
	print ("Comments downloading")
	page_info = requests.get(YOUTUBE_LINK.format(videoId = videoId, key = key))

	while page_info.status_code != 200:
		if page_info.status_code != 429:
			print ("Comments disabled")
			sys.exit()

		time.sleep(20)
		page_info = requests.get(YOUTUBE_LINK.format(videoId = videoId, key = key))

	page_info = page_info.json()

	comments = []
	co = 0;
	for i in range(len(page_info['items'])):
		comments.append(page_info['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'])
		co += 1
		if co == count:
			progress(co, count, cond = True)
			print ()
			return comments

	progress(co, count)
	# INFINTE SCROLLING
	while 'nextPageToken' in page_info:
		temp = page_info
		page_info = requests.get(YOUTUBE_IN_LINK.format(videoId = videoId, key = key, pageToken = page_info['nextPageToken']))

		while page_info.status_code != 200:
			time.sleep(20)
			page_info = requests.get(YOUTUBE_IN_LINK.format(videoId = videoId, key = key, pageToken = temp['nextPageToken']))
		page_info = page_info.json()

		for i in range(len(page_info['items'])):
			comments.append(page_info['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'])
			co += 1
			if co == count:
				progress(co, count, cond = True)
				print ()
				return comments
		progress(co, count)
	progress(count, count, cond = True)
	print ()

	return comments

def features(words):
	words = word_tokenize(words)

	scoreF = BigramAssocMeasures.chi_sq

	#bigram count
	n = 150

	bigrams = BCF.from_words(words).nbest(scoreF, n)

	return dict([word,True] for word in itertools.chain(words, bigrams))

def training():
	pos_sen = open("positive.txt", 'r', encoding = 'latin-1').read()
	neg_sen = open("negative.txt", 'r', encoding = 'latin-1').read()

	emoji = open("emoji.txt",'r', encoding = 'latin-1').read()
	pos_emoji = []
	neg_emoji = []
	for i in emoji.split('\n'):
		exp = ''
		if i[len(i)-2] == '-':
			for j in range(len(i) - 2):
				exp += i[j]
			neg_emoji.append(( {exp : True}, 'negative'))
		else:
			for j in range(len(i)-1):
				exp += i[j]
			pos_emoji.append(( {exp : True}, 'positive'))

	prev = [(features(words), 'positive') for words in pos_sen.split('\n')]
	nrev = [(features(words), 'negative') for words in neg_sen.split('\n')]
	
	pos_set = prev + pos_emoji
	neg_set = nrev + neg_emoji

	real_classifier = NaiveBayesClassifier.train(prev+nrev)

	# SAVE IN FILE TO AVOID TRAIINING THE DATA AGAIN
	save_doc = open("classifier.pickle", 'wb')
	pickle.dump(real_classifier, save_doc)
	save_doc.close()

	# TO TEST ACCURACY OF CLASSIFIER UNCCOMMENT THE CODE BELOW
	# ACCURACY : 78.1695423855964

	# ncutoff = int(len(nrev)*3/4)
	# pcutoff = int(len(prev)*3/4)
	# train_set = nrev[:ncutoff] + prev[:pcutoff] + pos_emoji + neg_emoji
	# test_set = nrev[ncutoff:] + prev[pcutoff:]
	# test_classifier = NaiveBayesClassifier.train(train_set)

	# print ("Accuracy is : ", util.accuracy(test_classifier, test_set) * 100)

  # import training_classifier as tcl
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize	
import os.path
import pickle
from statistics import mode
from nltk.classify import ClassifierI
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import BigramCollocationFinder as BCF
import itertools
from nltk.classify import NaiveBayesClassifier


def features(words):
	temp = word_tokenize(words)

	words = [temp[0]]
	for i in range(1, len(temp)):
		if(temp[i] != temp[i-1]):
			words.append(temp[i])

	scoreF = BigramAssocMeasures.chi_sq

	#bigram count
	n = 150

	bigrams = BCF.from_words(words).nbest(scoreF, n)

	return dict([word,True] for word in itertools.chain(words, bigrams))

class VoteClassifier(ClassifierI):
	def __init__(self, *classifiers):
		self.__classifiers = classifiers

	def classify(self, comments):
		votes = []
		for c in self.__classifiers:
			v = c.classify(comments)
			votes.append(v)
		con = mode(votes)

		choice_votes = votes.count(mode(votes))
		conf = (1.0 * choice_votes) / len(votes)

		return con, conf

def sentiment(comments):

  if not os.path.isfile('classifier.pickle'):
    training()

  fl = open('classifier.pickle','rb')
  classifier = pickle.load(fl)
  fl.close()

  pos = 0
  neg = 0
  for words in comments:
    comment = features(words)
    sentiment_value, confidence = VoteClassifier(classifier).classify(comment)
    if sentiment_value == 'positive':# and confidence * 100 >= 60:
      pos += 1
    else:
      neg += 1

  result={}
  result['positive']=pos * 100.0 /len(comments)
  result['negative']=neg * 100.0 /len(comments)
  return result