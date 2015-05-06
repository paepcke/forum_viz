
from pymysql_utils1 import MySQLDB
from topia.termextract import extract
#from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

class PostGetter:

  '''
  Initialize the class with the appropriate mysql instance.
  Initialize the DB instance to point to EdxForum.contents.
  '''
  def __init__(self):
	mysql_dbhost='localhost'
	mysql_user='root'#getpass.getuser()
	mysql_db='EdxForum'
	mysql_passwd=self.getmysqlpasswd()
	self.type='all'
	print('got passwd from file %s'%(mysql_passwd))
	self.db=MySQLDB('127.0.0.1',3306,'root','','EdxForum')
	
  '''
  Used only for testing. Test password provided.
  '''	
  def getmysqlpasswd(self):
    return '5PinkPenguines'

  '''
  Password is typically stored in ~user_name/.ssh/mysql
  '''
  def getMysqlPasswd():
    homeDir=os.path.expanduser('~'+getpass.getuser())
    f_name=homeDir+'/.ssh/mysql'
    with open(f_name, 'r') as f:
      password = f.readline().strip()
    print 'password got from file is %s'%(password)
    return password


  def getAllDataForCourseAsString(self,course):
	courseData=''
	query_string='select body from contents where course_display_name=\'%s\''%(course)
	for row in self.db.query(query_string):
		courseData += row[0]
	return courseData

  def getMinWeekForCourse(self, course):
    query_string='select min(YEARWEEK(created_at)) from contents where course_display_name=\'%s\''%(course)
    minval=0
    for row in self.db.query(query_string):
      minval=row[0]
    return int(minval)

  def getMaxWeekForCourse(self, course):
    query_string='select max(YEARWEEK(created_at)) from contents where course_display_name=\'%s\''%(course)
    maxval=0
    for row in self.db.query(query_string):
      maxval=row[0]
    return int(maxval)

  def getWeeklyDataForCourseAsString(self,course, week):
    courseData=''
    query_string='select body from contents where course_display_name=\'%s\' and YEARWEEK(created_at)=%s'%(course,week)
    for row in self.db.query(query_string):
      courseData += row[0]
    return courseData

  def getNumPosts(self, course, week):
    query_string='select count(*) from contents where course_display_name=\'%s\' and YEARWEEK(created_at)=%s'%(course,week)
    numPosts=0
    for row in self.db.query(query_string):
      numPosts=row[0]
    return int(numPosts)
    


"""   
def main():
  p=PostGetter()
  cname='Medicine/HRP258/Statistics_in_Medicine'
  text = p.getAllDataForCourseAsString(cname)
  print text
  extractor = extract.TermExtractor()
  rawData = sorted(extractor(text))
  cv = CountVectorizer(min_df=0, charset_error="ignore",stop_words="english", max_features=200)
  counts = cv.fit_transform([text]).toarray().ravel()
  words = np.array(cv.get_feature_names())
  words = words[counts > 1]
  counts = counts[counts > 1]



  for item in rawData:
  	if item[1] > 2 and item[2] < 2 :
          print item	

  print 'New one'        

  print words        

"""
#main()  
