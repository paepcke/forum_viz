from pymysql_utils1 import MySQLDB
from collections import defaultdict
from NaiveBayes import NaiveBayes
import pickle
import sys
import operator

import re

d=defaultdict (lambda:1)
d1=defaultdict (lambda:1)



def getdata(qq,code):
  happy_posts=[]
  for c in mydb.query(qq):
    obj=[];
    happy_posts.append(c[0])
    s=c[0]
    try:
      s=s.encode('ascii', 'ignore')
    except :
      s='z'

    if(s!='z'):
      t=(s,code)
      all_data.append(t)
      codes.append(code)
  return happy_posts


def getdata_test(qq,nb):
  happy_posts=[]
  ctr=0
  pos=0
  neg=0
  for c in mydb.query(qq):
    obj=[];
    happy_posts.append(c[0])
    s=c[0]
    try:
      s=s.encode('ascii', 'ignore')
    except :
      print s
      s='z'

    if(s!='z'):
      ctr=ctr+1
     # print s;
      x=nb.classify (s)
      if ('non' in x):
        neg=neg+1
      else:
        pos=pos+1
        
    print s
    print x
    print ctr  
    print pos
    print neg
    mydb.executeParameterized("update EdxForum.contents set confused = %s where created_at=%s and forum_uid = %s and sk=%s", (x,c[0],c[1],c[2]) );

  return happy_posts


def getFeatures(data):
    datapoint=[]
    data_parsed=re.findall(r"[\w']+|[,!?;]", data)
    for i in xrange(0,len(data_parsed)-1):
      if('redacted' in data_parsed[i]):
        continue  
      datapoint.append(data_parsed[i])
    #  datapoint.append(data_parsed[i]+"_"+data_parsed[i+1])

    return datapoint





def getdata1(qq,code,all_data,categories):
  #qq=qq+' limit 50'
  #for c in mydb.query("select body from EdxForum.contents where body like '%:)%'"):
  for c in mydb.query(qq):
    obj=[];
    s=c[0]
    try:
      s=s.encode('ascii', 'ignore')
    except :
      s='z'

    if(s!='z'):
      t=(s,code)
      all_data.append(s)
      categories.append(code)

mydb=MySQLDB('127.0.0.1',3306,'jagadish','5PinkPenguines','EdxForum')
mydb.execute('SET NAMES utf8;');
mydb.execute('SET CHARACTER SET utf8;');
mydb.execute('SET character_set_connection=utf8;');
if (len(sys.argv) !=2):
  print 'usage: python testgen.py test/train'
  sys.exit (1)



all_data=[]
codes=[]


happy=[]
qq="select body from EdxForum.contents where body like '%:)%' or body like '%:-)%' "
l=getdata(qq,0)
print len(l)
qq="select body from EdxForum.contents where body like '%:(%' or body like '%:-(%'  "
l=getdata(qq,1)
print len(l)

qq="select body from EdxForum.contents where body like '%confuse%' or body like '%confusing%' or body like '%confused%' or body like '%unclear%' or body like '%not clear%' or body like '%don''t understand%' or body like '%do not understand%' or body like '%do not get%'  "
l=getdata(qq,2)
print len(l)






mydb=MySQLDB('127.0.0.1',3306,'jagadish','5PinkPenguines','EdxForum')
mydb.execute('SET NAMES utf8;');
mydb.execute('SET CHARACTER SET utf8;');
mydb.execute('SET character_set_connection=utf8;');



train_data=[]
train_cat=[]
test_data=[]
test_cat=[]

qq="select body from EdxForum.contents where body like '%confused%' or body like '%confusion%' or body like '%not understand%' or body like '%don''t understand%' or body like '%not follow%' or body like '%don''t follow%' or body like '%quite understand%' or body like '%unclear to%' or body like '%can''t understand%'"

getdata1(qq,1,train_data,train_cat)


datapoints=[]
classes=[]

for data in train_data:
  datapoint=getFeatures(data)
  classes.append('confused')
  datapoints.append(datapoint)
  



sorted_x = sorted(d.iteritems(), key=operator.itemgetter(1))
print sorted_x


for tt in sorted_x:
  print ('%s %s\n'%( tt[0],tt[1] ))



sorted_x = sorted(d1.iteritems(), key=operator.itemgetter(1))
print sorted_x


for tt in sorted_x:
  print ('%s %s\n'%( tt[0],tt[1] ))






#print datapoints
print classes
print len(datapoints)
print len(classes)


data2=[]
cat2=[]
#qq="select body from EdxForum.contents where body like '%confused%' or body like '%not understand%' or body like '%don''t understand%' or body like '%not follow%' or body like '%don''t follow%' or body like '%quite understand%' or body like '%unclear to%' or body like '%can''t understand%'"
qq="select body from EdxForum.contents where body not like '%confused%' and body not like '%confusing%' and body not like '%confusion%' and body not like '%confusing%'  and body not like '%not understand%' and body not like '%don''t understand%' and body not like '%not follow%' and body not like '%don''t follow%' and body not like '%quite understand%' and body not like '%unclear to%' and body not like '%can''t understand%' and forum_uid > 1000 order by  RAND() limit 0,999"
getdata1(qq,1,data2,cat2)


#datapoints=[]
for data in data2:
  datapoint=getFeatures(data)
  print data
  classes.append('non_confused')
  datapoints.append(datapoint)

#print datapoints  
#print classes
#print 
print len(data2)
print len(datapoints)



nb = NaiveBayes()


tdatapoints = datapoints
tclasses = classes;

if ('test' in sys.argv[1]):
  print sys.argv[1]
  try:
     datapoints=pickle.load( open( "save.p", "rb" ) )
     classes=pickle.load( open( "save.p1", "rb" ) )
  except:
     datapoints = tdatapoints
     classes = tclasses
     print "reverting to stateless mode"   
else:
  pickle.dump( datapoints, open( "save.p", "wb" ) )
  pickle.dump( classes, open( "save.p1", "wb" ) )


print len(datapoints)
print len(classes)

if('train' in sys.argv[1]):
  print 'training done model saved to save.p and save.p1'
  sys.exit (0)

nb.addExamples(datapoints,classes)

tests=[]
tests.append(getFeatures('Your graphs were wrong. Please correct it'))
tests.append(getFeatures('thanks john :) I dont get it'))
tests.append(getFeatures("thanks for your answer"))
tests.append(getFeatures('I appreciate your honest response. thanks'))

tests.append(getFeatures('I am not sure how to implement this. Can a TA please clarify? We have been stuck on this problem for quite awhile'))
tests.append(getFeatures("I love them. I can't work on it now. I'm totally confused"))
tests.append(getFeatures("Is the 3 page length a hard limit. It was not clear in the assignment specification"))

tests.append(getFeatures("""
I have no clue about what this class is about. 
  """))
tests.append(getFeatures(
"""
Hi, the point of the questions is given a particular ranked list with P@10=0.5, if we change "Positions of relevant documents in the retrieved list", does P@10 change? If P@10 doesn't change then we say it does not capture that attribute.

"""
  ))
tests.append(getFeatures(
"""
Does it mean, is it trying to ask, if we increase or decrease number of relevant documents in the corpus, does the precision@10 change?

"""
  ))
tests.append(getFeatures(
"""
confused on how to compile and run the program
Is there a detailed instruction on how to compile and run the program? 
Where should I run the script? and also, shall we use eclipse to compile it?

"""
  ))
tests.append(getFeatures(
"""
I'm very confused about the difference between BSBI and SPIMI. My understanding is that: BSBI is that first you have blocks, and in each block, you keep a dictionary(termID, Document ID mapping) and sort them, so in each block, we have different inverted index. Finally, we merge all the inverted index across the blocks. SPIMI is similar to BSBI. The only difference is that in SPIMI, we don't sort termID in the blocks. Do I understand these two algo correctly? Can anyone explain the difference between the two? Thanks

"""
  ))
tests.append(getFeatures(
"""
The algorithm you described is SPIMI.
 
SPIMI:
Local (to block) dictionaries.
As the title says: Single-pass in-memory indexing, SPIMI consumes each block and creates and inverted index for it and writes it out. Then, it merges all the inverted indices across all the blocks.
 
BSBI:
Global dictionaries. (termID, documentID mapping)
BSBI consumes each block and sorts it. Then, it merges all the sorted runs and creates the index out of it.

"""
  ))
tests.append(getFeatures(
"""
I went further into reading (Ch. 2) but still confused about something:
 
When no stemming is used does that indirectly affect normalizing? 
 
Also, If a punctuation is dropped from the middle of the word does it remain one word or is it divided into two tokens? 

"""
  ))
tests.append(getFeatures(
"""
The first programming assignment is available on Coursera under the "Programming Assignments" tab (https://stanford.coursera.org/cs276-002/assignment).
 
PA1 is due at midnight (11:59pm) Thursday April 17, 2014.

"""
  ))

tests.append(getFeatures(
"""
This is for task 1--it's a very simple model--task 2 addresses exactly this issue.


"""
  ))
tests.append(getFeatures(
"""
Hi Alan,
I still cannot relate to the answer you have given. If that is the case, then are we implementing a modification of cosine similarity, just to handle the issue in bm25?


"""
  ))

tests.append(getFeatures(
"""
Yes, thanks Alan. I think it makes more sense now that we are doing this in task 1 just to have a baseline for task 2, though this is the not the most accurate normalization we are supposed to do in case of cosine similarity.
Though I did not post the original question, but having a common doubt I posted with a follow up and it surely helped.

"""
  ))

tests.append(getFeatures(
"""
Your explanation for the choice of using body length still does not make sense to me.  I thought the point of the project was to compare the ranking power of cosine similarity and bm25.  Is this a valid comparison if cosine similarity is handicapped by a poor choice of normalization? Is cosine similarity always worse than bm25?


"""
  ))

tests.append(getFeatures(
"""

I have a question around the method
 
public Map<String,Map<String, Double>> getDocTermFreqs(Document d, Query q)
 
The PA3 write up says we only care about the terms that are there in the Query, which means we should be creating "map from tf type -> queryWord -> score" then why there is a loop in the last to increase relevant counts? Is it to handle case where Query can have same term more than once?
 

"""
  ))

tests.append(getFeatures(
"""
How does one incorporate the Vj Function to incorporate PageRank (f)? 
 
from instructions: https://d396qusza40orc.cloudfront.net/cs276/assignments/pa3/pa3.pdf 
 
equations 2 & 3 were used calculated by term, field/zone over all documents.
 
We revisit pagerank in equation 4.  Is the Vj function an average of pageranks of all documents or some other calculation?  
 


"""
  ))

tests.append(getFeatures(
"""
A little confused where in the code to apply Laplace smoothing for the construction of the query vector.
 
IDFs are calculated prior to query evaluation based on the corpus and stored in a map. When we construct the query vector, we retrieve the IDF for a query term and multiply it by the term frequency. In the case the IDF of the term is not in the map then we assume it is 0 and therefore the element in the query vector becomes 0.
 
So where do we apply the add-one smoothing, since we should not access the corpus again when constructing the query vectors?

"""
  ))

tests.append(getFeatures(
"""
It may help a bit by writing a script and automating an exhaustive search over a reasonable range and let it run for a night. Then you'll get some reasonably tuned parameters. 


"""
  ))

tests.append(getFeatures(
"""
In the Term Frequency Section 5.2 of the PA3 handout, it states:
The raw term frequencies can be computed using the query (should be 1 for most queries but not necessarily true).
 
Under what circumstances will the raw term frequency for the query not be one? Should we account for the case when a query may have a repeating word - e.g., "stanford math stanford"? Would the raw term frequency for this case be [2 1]?


"""
  ))
tests.append(getFeatures(
"""
https://stanford.coursera.org/cs276-002/assignment/view?assignment_id=27
 
"Please download skeleton code (data is in here and instructions from here.)"
 
Both link to the instruction page. Link to skeleton code is missing !
 
Could the team fix it. Thanks !


"""
  ))
tests.append(getFeatures(
"""
We have packed PA3 with new data consisting of queries suggested and rated by you. The data contains a more varied set of urls (from the top 50 results returned by a search engine) for each query as compared to those from last year (using the top 10 results). Hopefully, that will help you better tune and debug your system.
 
We have also updated the data section in the writeup describing how we split the data into training and development sets. This will help you avoid overfitting and provide a consistent way of comparing performances among students. Please read that section carefully as we require you to report performances on both the training and development sets.
 


"""
  ))
tests.append(getFeatures(
"""
The question asks which attributes it DOES NOT capture. It also says. Please put the numbers in ascending order. 
So if metric m captures some info about atrribute a1 a little lesser about a2 and nothing about a3. How should I order it ? 


"""
  ))
tests.append(getFeatures(
"""
The following function is provided to build the idf from the corpus of pa1. This function takes a directory pointing to the corpus and the resulting serialized idfFile. 
 
//builds and then serializes from file
public static Map<String,Double> buildDFs(String dataDir, String idfFile)
 
As the Rank.java (./rank.sh <inputDataFile> <taskId>) is supposed to take two parameters, how would be provide the path for the pa1 corpus?
 
I can hardcode this for development but this won't work when run on corn machine by the final script?
 
Am I missing something?


"""
  ))
tests.append(getFeatures(
"""
For this question, do we approach it by the following steps:
 
1) For a given follower, compute the Euclidean distances between that and each of the three leaders, and follow the leader with the smallest Euclidean distance
 
2) Query is matched to the leader with the largest cosine similarity value.
 
3) Retrieve documents.
 
However I approached this question by these steps and got it wrong. Am I missing something here??


"""
  ))
tests.append(getFeatures(
"""
A little bit confusion . In the instructions , it appears the anchor field indicates how many times the anchor contain the query term , so even the term appears twice in the same anchor , it should only count once ? Does this make sense ?


"""
  ))
tests.append(getFeatures(
"""
The document length is 125, you don't need to know anything about whether or not they are unique.


"""
  ))

tests.append(getFeatures(
"""
Sorry, but a CS executive committee meeting conflicts with my Tue 2-3 office hours today.  The meeting may be done by 2:30, so I will hopefully be in my office for the end part of the session, but it could overrun all of it.  If you'd like to talk to me about something, you can catch me after class, or send me email and we can find a time.

"""
  ))
tests.append(getFeatures(
"""
how do we construct top documents for each term? by the highest coordinate for that term?
 then, first tiers of both words has empty cross. so, there is no advantage of using tiers...
 
 
What is wrong in my logic?


"""
  ))
tests.append(getFeatures(
"""
We just uploaded the tutorial video for PA3 on Coursera under Tutorial in video lectures. Hope it can help you get started!

"""
  ))
tests.append(getFeatures(
"""
This assignment has been highly confusing and SCPD students did not get any notice either. The due date was so short, not falling on a Thursday and now would we be penalized with the late days even if we have not applied for "late days"?
 
This has added more confusion now. Can we at least know how many late days we have? Is there a place to check for it?
"""
  ))
tests.append(getFeatures(
"""
Given the vector length has been normalized to 1,  these two can be used interchangeably, as long as keep the calculation consistent
"""
  ))
tests.append(getFeatures(
"""
Are there any plans to provide access to sample or previous exam papers?
 
I would be interested in knowing the format and style of the questions.

"""
  ))
tests.append(getFeatures(
"""
I'd say, it all depends on your implementation. If your implementation is very tuned to perform well on the dev queries, it may or may not perform well on the other set(as it's tuned for the given queries). If it's not, then it most likely will produce results in the same ball park. I'd suggest to close all loopholes (if there are any) in your code. Try running it for half the queries and tune it, then run it for the whole set and compare and retune.

"""
  ))


getdata_test ("select body,created_at,forum_uid,sk from EdxForum.contents",nb)


for test in tests:
  x=nb.classify(test)
  print test
  print x






