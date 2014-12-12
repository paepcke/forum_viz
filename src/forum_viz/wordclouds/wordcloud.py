# Author: Andreas Christian Mueller <amueller@ais.uni-bonn.de>
# (c) 2012
#
# License: MIT

import random
import os
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from postgetter import PostGetter
from topia.termextract import extract
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from query_integral_image import query_integral_image
from collections import defaultdict
import operator
from collections import Counter

FONT_PATH = "/System/Library/Fonts/DroidSansMono.ttf"


def make_wordcloud(words, counts, fname, font_path=None, width=400, height=200,
                   margin=5, ranks_only=False):
    """Build word cloud using word counts, store in image.

    Parameters
    ----------
    words : numpy array of strings
        Words that will be drawn in the image.

    counts : numpy array of word counts
        Word counts or weighting of words. Determines the size of the word in
        the final image.
        Will be normalized to lie between zero and one.

    font_path : string
        Font path to the font that will be used.
        Defaults to DroidSansMono path.

    fname : sting
        Output filename. Extension determins image type
        (written with PIL).

    width : int (default=400)
        Width of the word cloud image.

    height : int (default=200)
        Height of the word cloud image.

    ranks_only : boolean (default=False)
        Only use the rank of the words, not the actual counts.

    Notes
    -----
    Larger Images with make the code significantly slower.
    If you need a large image, you can try running the algorithm at a lower
    resolution and then drawing the result at the desired resolution.

    In the current form it actually just uses the rank of the counts,
    i.e. the relative differences don't matter.
    Play with setting the font_size in the main loop vor differnt styles.

    Colors are used completely at random. Currently the colors are sampled
    from HSV space with a fixed S and V.
    Adjusting the percentages at the very end gives differnt color ranges.
    Obviously you can also set all at random - haven't tried that.

    """
    if len(counts) <= 0:
        print("We need at least 1 word to plot a word cloud, got %d."
              % len(counts))

    if font_path is None:
        font_path = FONT_PATH

    if not os.path.exists(font_path):
        raise ValueError("The provided font %s does not exist." % font_path)

    # normalize counts
    counts = counts / float(counts.max())
    # sort words by counts
    inds = np.argsort(counts)[::-1]
    counts = counts[inds]
    words = words[inds]
    # create image
    img_grey = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img_grey)
    integral = np.zeros((height, width), dtype=np.uint32)
    img_array = np.asarray(img_grey)
    font_sizes, positions, orientations = [], [], []
    # intitiallize font size "large enough"
    font_size = 1000
    # start drawing grey image
    for word, count in zip(words, counts):
        # alternative way to set the font size
        if not ranks_only:
            font_size = min(font_size, int(100 * np.log(count + 100)))
        while True:
            # try to find a position
            font = ImageFont.truetype(font_path, font_size)
            # transpose font optionally
            orientation = random.choice([None, Image.ROTATE_90])
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            draw.setfont(transposed_font)
            # get size of resulting text
            box_size = draw.textsize(word)
            # find possible places using integral image:
            result = query_integral_image(integral, box_size[1] + margin,
                                          box_size[0] + margin)
            if result is not None or font_size == 0:
                break
            # if we didn't find a place, make font smaller
            font_size -= 1

        if font_size == 0:
            # we were unable to draw any more
            break

        x, y = np.array(result) + margin // 2
        # actually draw the text
        draw.text((y, x), word, fill="white")
        positions.append((x, y))
        orientations.append(orientation)
        font_sizes.append(font_size)
        # recompute integral image
        img_array = np.asarray(img_grey)
        # recompute bottom right
        # the order of the cumsum's is important for speed ?!
        partial_integral = np.cumsum(np.cumsum(img_array[x:, y:], axis=1),
                                     axis=0)
        # paste recomputed part into old image
        # if x or y is zero it is a bit annoying
        if x > 0:
            if y > 0:
                partial_integral += (integral[x - 1, y:]
                                     - integral[x - 1, y - 1])
            else:
                partial_integral += integral[x - 1, y:]
        if y > 0:
            partial_integral += integral[x:, y - 1][:, np.newaxis]

        integral[x:, y:] = partial_integral

    # redraw in color
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    everything = zip(words, font_sizes, positions, orientations)
    for word, font_size, position, orientation in everything:
        font = ImageFont.truetype(font_path, font_size)
        # transpose font optionally
        transposed_font = ImageFont.TransposedFont(font,
                                                   orientation=orientation)
        draw.setfont(transposed_font)
        draw.text((position[1], position[0]), word,
                  fill="hsl(%d" % random.randint(0, 255) + ", 80%, 50%)")
    img.show()
    img.save(fname)

def loadstopwords (filen):
  f = open(filen,'r')
  stopw = set()
  for line in f:
    if len(line)>0 and line != '':
      stopw.add(line.strip())
  print stopw  
  return stopw  



def getWordCounts (text, f1, f2, smartStopWords):
  extractor = extract.TermExtractor()

  rawData = sorted(extractor(text), key=lambda x: x[1], reverse = True)
  """cv = CountVectorizer(min_df=0, charset_error="ignore",stop_words="english", max_features=200000000)
  counts = cv.fit_transform([text]).toarray().ravel()
  words = np.array(cv.get_feature_names())
  words = words[counts > 4]
  counts = counts[counts > 4]"""



  for item in rawData:
    if item[1] > 2 and item[2] < 2 :
          print item    

  #raw_input ('beg')

  tags = extractor.tagger(text)
  print text

  print tags

  tagsDict = {}

  for tag in tags:
    tagsDict[tag[0]] = tag[1]

  stopwords = set()
  f = open ('stopwords1','r')
  for line in f:
    stopwords.add(line.strip())

  w = []
  c = []  
    

  print "********"          

  ff = open(f1,'w')
  ff1 = open(f2,'w')
  wordcountDict = defaultdict(lambda:0)

  for item in rawData:
    #take all unigrams occuring more than two times
    if item[1] > 2 and item[2] < 2 :
          if item[0] in tagsDict and 'NN' in tagsDict[item[0]] and item[0] not in stopwords and item[0] and item[0][0].isalpha():
            print '%s %s'%(item[0], item)
            w.append(item[0])
            c.append(item[1])
            #ff.write('%s(%s)\n'%(item[0],item[1]))
            ff.write('%s\n'%(item[0]))
            wordcountDict[item[0]]=item[1]
          if item[0] in tagsDict and 'NN' in tagsDict[item[0]] and  item[0] and item[0][0].isalpha():
            ff1.write('%s\n'%(item[0]))




  w_ = np.asarray(w)
  c_ = np.asarray(c)


  print c_

  ff.close()
  ff1.close()


  return wordcountDict,w_,c_


def getWordCountsAdj (text, f1, f2, smartStopWords):
  extractor = extract.TermExtractor()

  rawData = sorted(extractor(text), key=lambda x: x[1], reverse = True)
  """cv = CountVectorizer(min_df=0, charset_error="ignore",stop_words="english", max_features=200000000)
  counts = cv.fit_transform([text]).toarray().ravel()
  words = np.array(cv.get_feature_names())
  words = words[counts > 4]
  counts = counts[counts > 4]"""



  for item in rawData:
    if item[1] > 2 and item[2] < 2 :
          print item    

  #raw_input ('beg')

  tags = extractor.tagger(text)
  print text

  print tags

  tagsDict = {}

  for tag in tags:    
    tagsDict[tag[0]] = tag[1]

  stopwords = set()
  f = open ('stopwords1','r')
  for line in f:
    stopwords.add(line.strip())

  w = []
  c = []  
    

  print "********"          

  ff = open(f1,'w')
  ff1 = open(f2,'w')
  wordcountDict = defaultdict(lambda:0)
  stopwords = loadstopwords('a')
  poswords = loadstopwords ('pos.txt')
  negwords = loadstopwords ('neg.txt')
  print 'stop words'

  
  for item in rawData:
    #take all unigrams occuring more than two times
          if item[0] in tagsDict and ('JJ' in tagsDict[item[0]] or 'VB' in tagsDict[item[0]])and item[0] not in stopwords and item[0] and item[0][0].isalpha():
            print '%s %s'%(item[0], item)
            w.append(item[0])
            c.append(item[1])
            #ff.write('%s(%s)\n'%(item[0],item[1]))
            ff.write('%s\n'%(item[0]))
            wordcountDict[item[0]]=item[1]
          if item[0] in tagsDict and 'NN' in tagsDict[item[0]] and  item[0] and item[0][0].isalpha():
            ff1.write('%s\n'%(item[0]))




  w_ = np.asarray(w)
  c_ = np.asarray(c)

  print w
  print tags

  items = []
  for tag in tags:
    pos = tag[1] 
    if  tag[0] in poswords or tag[0] in negwords:
      items.append(tag[0])


  
  print items

  w1 = []
  c1 = []
  wdict = {}


  word_freq = Counter(items)
  for word, freq in word_freq.most_common():
    print ("%-10s %d" % (word, freq))
    w1.append(word)
    c1.append(freq)
    wdict[word] = freq


  w_ = np.asarray(w1)
  c_ = np.asarray(c1)


  raw_input('Hello world')


  print c_

  ff.close()
  ff1.close()


  return wdict,w_,c_


def generateWC (w_, c_, f1):  
  make_wordcloud(w_, c_, "%s.png"%f1)

def generateWeeklyWCAdj (cname, prefix, smartStopWords):
  p = PostGetter()
  minWeek = p.getMinWeekForCourse(cname)
  maxWeek = p.getMaxWeekForCourse(cname)
  for week in range(minWeek, maxWeek+1):
    numPosts = p.getNumPosts(cname, week)
    if (numPosts < 20):
      continue
    #text = p.getAllDataForCourseAsString(cname)  
    text=p.getWeeklyDataForCourseAsString(cname, week)
    num = (week-minWeek)
    (wordcountDict, w_, c_)=getWordCountsAdj(text,'%s_week%s_stopADJ'%(prefix,week),'%s_week%s'%(prefix, week), smartStopWords)
    generateWC(w_,c_,'%s_adjweek%s_stop'%(prefix,week))



def generateWeeklyWC (cname, prefix, smartStopWords):
  p = PostGetter()
  minWeek = p.getMinWeekForCourse(cname)
  maxWeek = p.getMaxWeekForCourse(cname)
  for week in range(minWeek, maxWeek+1):
    numPosts = p.getNumPosts(cname, week)
    if (numPosts < 20):
      continue
    text=p.getWeeklyDataForCourseAsString(cname, week)
    num = (week-minWeek)
    (wordcountDict, w_, c_)=getWordCounts(text,'%s_week%s_stop'%(prefix,week),'%s_week%s'%(prefix, week), smartStopWords)
    generateWC(w_,c_,'%s_week%s_stop'%(prefix,week))

def dictToArray (x):
  x_sorted = sorted(x.items(), key=operator.itemgetter(1))
  ww=[]
  cc=[]
  for w,c in x_sorted :
    ww.append(w)
    cc.append(c)
  print ww
  print cc
  return np.asarray(ww),np.asarray(cc)

def getDiff (dict1, dict2):
  print dict1
  print dict2
  dict3 = defaultdict(lambda:0)
  for key2 in dict2:
    if key2 not in dict1:
      print 'boo'
      dict3[key2] = dict2[key2]
    else:
      print 'foo'
  print 'dict3'    
  print dict3    
  return dict3   

def weightWords (dict1, dict2, penalty):
  print dict1
  print dict2
  dict3 = defaultdict(lambda:0)
  for key2 in dict2:
    if key2 not in dict1:
      dict3[key2] = dict2[key2]
    else:
      dict3[key2] = dict2[key2]*0.5
  print 'dict3'    
  print dict3
  return dict3   


def generatePenalizeWeeklyWindows (cname, prefix, diff):
  p = PostGetter ()
  minWeek = p.getMinWeekForCourse (cname)
  maxWeek = p.getMaxWeekForCourse (cname)

  d = {}
  for week in range(minWeek, maxWeek):
    currText = p.getWeeklyDataForCourseAsString(cname, week)
    smartStopWords = True
    (currWordCountDict, currw_, currc_) = getWordCounts(currText,'%s_week%s_stop'%(prefix,week),'%s_week%s'%(prefix, week), smartStopWords)
    d[week] = currWordCountDict

  for week in range(minWeek+1, maxWeek):
    currWordCountDict = d[week]

    if week == 201412:
      print "CURRRRRRRRRRRRR"
      #raw_input('bar')
      print currWordCountDict
      #raw_input ('foo')

    ctr=diff
    for i in range (week-1, minWeek-1,-1) :
      ctr= ctr-1
      if (ctr == 0):
        break
      prevDict = d[i]
      diffDict = weightWords (prevDict, currWordCountDict, 0.5)
      currWordCountDict = diffDict
      print currWordCountDict
      if week == 201412:
        #raw_input ('aa')
        print currWordCountDict
        #raw_input ('aa')

    if week == 201412:
      print "CURRRRRRRRRRRRR"
      #raw_input('end')
      print currWordCountDict
      #raw_input ('end')
    
      
    (w_,c_)=dictToArray (diffDict)
    print w_
    print c_
    print diff

    if (len(w_) > 3): 
      generateWC(w_,c_,'%s_week%s_stop_DIFF_EXP_PENALTY_DIFF%s'%(prefix,week,diff))
  










def generatePenalizeWeeks (cname, prefix, diff):
  p = PostGetter ()
  minWeek = p.getMinWeekForCourse (cname)
  maxWeek = p.getMaxWeekForCourse (cname)
  for week in range(minWeek, maxWeek):
    curr = week
    next = week+1
    currNumPosts = p.getNumPosts(cname, curr)
    nextNumPosts = p.getNumPosts(cname, next)
    if (currNumPosts < 20 or nextNumPosts < 20):
      continue
    currText = p.getWeeklyDataForCourseAsString(cname, curr)
    nextText = p.getWeeklyDataForCourseAsString(cname, next)
    smartStopWords = True

    (currWordCountDict, currw_, currc_) = getWordCounts(currText,'%s_week%s_stop'%(prefix,curr),'%s_week%s'%(prefix, curr), smartStopWords)
    (nextWordCountDict, nextw_, nextc_) = getWordCounts(nextText,'%s_week%s_stop'%(prefix,next),'%s_week%s'%(prefix, next), smartStopWords)
    penalty = 0.5
    diffDict = weightWords (currWordCountDict, nextWordCountDict , penalty)
    (w_,c_)=dictToArray (diffDict)
    generateWC(w_,c_,'%s_week%s_stop_DIFFPENALTY%s'%(prefix,week+1,diff))





def generateDiffConfigurableWeeks (cname, prefix, diff):
  p = PostGetter ()
  minWeek = p.getMinWeekForCourse (cname)
  maxWeek = p.getMaxWeekForCourse (cname)
  for week in range(minWeek, maxWeek):
    curr = week
    next = week+diff
    if next > maxWeek:
      break
    currNumPosts = p.getNumPosts(cname, curr)
    nextNumPosts = p.getNumPosts(cname, next)
    if (currNumPosts < 20 or nextNumPosts < 20):
      continue

    nextText = p.getWeeklyDataForCourseAsString (cname, next)
    smartStopWords = True
    (nextWordCountDict, nextw_, nextc_) = getWordCounts(nextText,'%s_week%s_stop'%(prefix,next),'%s_week%s'%(prefix, next), smartStopWords)

    for i in range (curr, next):
      currText = p.getWeeklyDataForCourseAsString(cname, i)
      (currWordCountDict, currw_, currc_) = getWordCounts(currText,'%s_week%s_stop'%(prefix,i),'%s_week%s'%(prefix, i), smartStopWords)
      diffDict = getDiff (currWordCountDict, nextWordCountDict)
      nextWordCountDict = diffDict

    (w_,c_)=dictToArray (diffDict)
    generateWC(w_,c_,'%s_week%s_stop_DIFFCONF%s'%(prefix,week+1,diff))



def generateDiff (cname, prefix, smartStopWords):    
  p = PostGetter()
  minWeek = p.getMinWeekForCourse(cname)
  maxWeek = p.getMaxWeekForCourse(cname)
  for week in range(minWeek, maxWeek):
    curr = week
    next = week+1
    currNumPosts = p.getNumPosts(cname, curr)
    nextNumPosts = p.getNumPosts(cname, next)
    if (currNumPosts < 20 or nextNumPosts < 20):
      continue
    currText = p.getWeeklyDataForCourseAsString(cname, curr)
    nextText = p.getWeeklyDataForCourseAsString(cname, next)

    (currWordCountDict, currw_, currc_) = getWordCounts(currText,'%s_week%s_stop'%(prefix,curr),'%s_week%s'%(prefix, curr), smartStopWords)
    (nextWordCountDict, nextw_, nextc_) = getWordCounts(nextText,'%s_week%s_stop'%(prefix,next),'%s_week%s'%(prefix, next), smartStopWords)
    diffDict = getDiff (currWordCountDict, nextWordCountDict)
    (w_,c_)=dictToArray (diffDict)
    generateWC(w_,c_,'%s_week%s_stop_DIFF'%(prefix,week+1))



  




def main():
  p=PostGetter()
  #cname='Engineering/CVX101/Winter2014'
  #cname='Education/EDUC115N/How_to_Learn_Math'
  #cname = 'Medicine/HRP258/Statistics_in_Medicine'
  if len(sys.argv) < 2:
    print 'Usage: python wordcloud.py <cname> sample course names: Engineering/CVX101/Winter2014,Medicine/HRP258/Statistics_in_Medicine' 
    sys.exit(1)

  cname = sys.argv[1]

  text = p.getAllDataForCourseAsString(cname)
  print text
  smartStopWords = True

  #(wordcountDict,w_,c_)=getWordCounts(text,'wc_cvx_full_stop','wc_cvx_full', smartStopWords)
  #generateWC(w_,c_,'wc_cvx_full_stop')
  #generateWeeklyWC(cname, 'WEEKLYwc_cvx', smartStopWords)
  #generateDiff (cname,'WEEKL_DIFF_lmath', smartStopWords)
  #generateDiffConfigurableWeeks (cname,'WEEKLZ_CONFDIFFwc_cvx',3)
  #generatePenalizeWeeks (cname, 'PENALIZE_PREVwc_cvx', 3)
  #generatePenalizeWeeklyWindows (cname, 'PENALIZE_morewc_cvx', 3)
  generateWeeklyWCAdj (cname, 'ADJwc_cvx', smartStopWords)

main()


"""
if __name__ == "__main__":

    from sklearn.feature_extraction.text import CountVectorizer

    if "-" in sys.argv:
        lines = sys.stdin.readlines()
        sources = ['stdin']
    else:
        sources = ([arg for arg in sys.argv[1:] if os.path.exists(arg)]
                   or ["constitution.txt"])
        lines = []
        for s in sources:
            with open(s) as f:
                lines.extend(f.readlines())

    p = PostGetter()        
    text = p.getAllDataForCourseAsString('HumanitiesScience/StatLearning/Winter2014')

    cv = CountVectorizer(min_df=1, charset_error="ignore",
                         stop_words="english", max_features=60000000)
    counts = cv.fit_transform([text]).toarray().ravel()
    words = np.array(cv.get_feature_names())
    # throw away some words, normalize
    words = words[counts > 4]
    counts = counts[counts > 4]
    output_filename = (os.path.splitext(os.path.basename(sources[0]))[0]
                       + "_.png")




    print words
    print counts

    counts = make_wordcloud(words, counts, output_filename)
"""