import os  
import collections

class IndexBuilder:

	def __init__(self, filename):
		self.dirname = filename
		self.index = collections.defaultdict(lambda:[])
		self.buildIndex()
	
	def buildIndex (self):
		for fn in self.absoluteFilePaths(self.dirname):
			print fn
        		videoid = fn
       			with open(fn) as f:
				print fn
				while True:
					try:
       						line1 = next(f)
						if not line1:
							break
						if '-->' in line1:
							splits = line1.split('-->')
							line2 = next(f)
							if not line2:
								break
							words = line2.split()
							for word in words:
								self.index[word].append((videoid, splits[0], splits[1]))
												
							print fn
					
					except StopIteration:
						break;
	def absoluteFilePaths(self,directory):
	   for dirpath,_,filenames in os.walk(directory):
       		for f in filenames:
           		yield os.path.abspath(os.path.join(dirpath, f))

	def getMinutes(self,word):
		return self.index[input]	

	def getVideoContentAsString(self, files):
		s = ''
		for filename in files:
			f = open(filename)
			while True:
				try:
						line1 = next(f)
						if not line1:
							break
						if '-->' in line1:
							line2 = next(f)
							if not line2:
								break
							words = line2.split()
							for word in words:
								s+=word+' '
		return s						



def main():		
	path = '/Users/jag/Downloads/Stanford medstats'
	i = IndexBuilder(path)
	print 'Index Building completed'
	input1 = path+'/BWH Module 1   Intro to Course   HD 1080p.srt'
	print i.getVideoContentAsString([input1])

	#while input != 'exit':
	#	input = raw_input('Enter a word (exit to end the program)')
	#	print i.getMinutes(input)

		
	
main()	
