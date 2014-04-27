import mysqldb
import getpass


def main():
	password = getpass.getpass("Password: ")
	outfile = raw_input("Output file prefix: ")
	course_name = raw_input("Course name: ")	
	db = mysqldb.MySQLDB('datastage.stanford.edu', user='akshayka', passwd=password, db='EdxPrivate')
	file_suffix = 0
	for result in db.query(
		'select body from ForumRaw where course_display_name="' + \
			course_name + '" limit 10'):
		result_str = str(result)
		f = open(outfile + str(file_suffix), 'w')
		f.write(result_str[result_str.index('\'') + 1:result_str.rindex('\'')].strip('\n'))
		f.close()
		file_suffix += 1

if __name__ == "__main__":
    main()
