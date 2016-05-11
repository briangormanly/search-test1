#!/usr/bin/python
from google import search
from google import get_page
import sys
import MySQLdb
import extraction
import requests
import BeautifulSoup

print(len(sys.argv))

if(len(sys.argv) > 1):
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
    #print ("hi")
    html = requests.get(url).text
    extracted = extraction.Extractor().extract(html, source_url=url)
    sqlString = "insert into searchResults (url, search, title, description, imageUrl, content, feeds, rating) values (%s, %s, %s, %s, %s, %s, %s, %s);"
    #print extracted.title, extracted.description, extracted.image, extracted.url
    
    soup = BeautifulSoup.BeautifulSoup(html)
    pageContent = "";
    for node in soup.findAll('p'):
      pageContent+=''.join(node.findAll(text=True))
    
    #print pageContent
    cur.execute(sqlString, (url, sys.argv[1], extracted.title, extracted.description, extracted.image, pageContent, str(extracted.feeds), 1.0))
    db.commit()
    #print(extracted)

  cur.close()