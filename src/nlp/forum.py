import mysqldb

# A struct of sorts that holds information field values
# for a given post (e.g. body, author_id), depending on the query.
class Post:
	pass

# An interface to a forum database. Performs database queries
# and returns formatted results.
class Forum:
	def __init__(self, host, user, passwd, db):
		self.db = mysqldb.MySQLDB(host, user=user, passwd=passwd, db=db)

	# Returns a list of Post structures, where each Post contains information
	# about a given post retrieved from the specificed table.
	#
	# More concretely, for each field in attr, there exists a corresponding
	# member variable in Post with the same name that contains that field's value.
	#
	# For example, if post_contents were called with
	# 	attr=['author_id', 'body'],
	# then each post p in posts would have
	#	p.author_id
	#	p.body
	# as valid members variables.
	def post_contents(self, table, course_name, attr=['body'], verbose=False):
		posts = []
		fields = ','.join(attr)
		for result in self.db.query(
			'select ' + fields + ' from ' + table + ' where course_display_name="' + \
				course_name + '"'):

			if (verbose):
				result_str = ''
				for entry in result: result_str += str(entry) + ' '
				print result_str

			post = Post()
			for i in range(0, len(attr)):
				setattr(post, attr[i], result[i])
			posts.append(post)

		return posts

if __name__ == "__main__":
    main()
