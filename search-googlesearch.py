#!/usr/bin/python

from google import search
from google import get_page
import sys
import MySQLdb

print(len(sys.argv))

if( len(sys.argv) > 1 ):
	db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="google_test1")        # name of the data base
	# you must create a Cursor object. It will let
	#  you execute all the queries you need
	cur = db.cursor()
	print(sys.argv[1])
	for url in search(sys.argv[1], stop=8):
		print(url)
		#print( get_page(url))
		#sqlString = "insert into searchResults (url, content) values ('" + url + "', '" + get_page(url) + "')"
		sqlString = "insert into searchResults (url, content) values (%s, %s);"
		#print(sqlString)
		cur.execute(sqlString, (url, get_page(url)))
		db.commit()

	cur.close()
