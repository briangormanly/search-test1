#!/usr/bin/python
from google import search
from google import get_page
from collections import Counter
import re
import sys
import MySQLdb
import extraction
import requests
import BeautifulSoup

print(len(sys.argv))

pronouns = '[all, another, any, anybody, anyone, anything, both, each, either, everybody, everyone, everything, few, he, her, hers, herself, him, himself, his, i, it, its, itself, little, many, me, mine, more, most, much, my, myself, neither, nobody, none, nothing, one, other, others, our, ours, ourselves, several, she, some, somebody, someone, something, that,their, theirs, them, themselves, these, they, this, those, us, we, what, whatever, which, whichever, who, whoever, whom, whomever, whose, you, your, yours, yourself, yourselves]'

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
    sqlString = "insert into searchResults (url, search, title, description, imageUrl, content, feeds, rating, searchWordCount, friendwordCount) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    #print extracted.title, extracted.description, extracted.image, extracted.url
    
    soup = BeautifulSoup.BeautifulSoup(html)
    pageContent = "";
    for node in soup.findAll('p'):
      pageContent+=''.join(node.findAll(text=True))
    
    #count the occurances of the search word in the site and weighted total (url = n*5, title = v*3, description v*2, content = v*1)
    titleSearchWordCount=url.lower().count(sys.argv[1].lower()) *5
    titleSearchWordCount+=extracted.title.lower().count(sys.argv[1].lower()) *3
    titleSearchWordCount+=extracted.description.lower().count(sys.argv[1].lower()) *2
    titleSearchWordCount+=pageContent.lower().count(sys.argv[1].lower())
    
    #count all the words in the text to find friendly words
    rawDescription = re.findall(r'\w+', (extracted.description))
    print(pageContent)
    rawContent = re.findall(r'\w+', (pageContent))
    print(rawDescription)
    rawDescriptionMinusPronouns = list(set(rawDescription) - set(pronouns))
    print(rawDescriptionMinusPronouns)
    descriptionWords = Counter(rawDescription)
    contentWords = Counter(rawContent)
    
    print()
    #print(descriptionWords)
    #print(contentWords)
    
    #print pageContent
    cur.execute(sqlString, (url, sys.argv[1], extracted.title, extracted.description, extracted.image, pageContent, str(extracted.feeds), 1.0, titleSearchWordCount, 1))
    db.commit()
    #print(extracted)

  cur.close()