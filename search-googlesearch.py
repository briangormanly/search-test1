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

discard = '[a, all, another, and, any, anybody, anyone, anything, are, be, both, by, each, either, everybody, everyone, everything, few, for, get, has, he, her, hers, herself, him, himself, his, i, it, its, itself, little, many, me, mine, more, most, much, my, myself, nbsp, neither, nobody, none, nothing, of, one, other, others, our, ours, ourselves, several, she, some, somebody, someone, something, that,their, theirs, them, themselves, these, the, they, this, those, to, us, was, we, what, whatever, which, whichever, while, will, who, whoever, whom, whomever, whose, with, you, your, yours, yourself, yourselves]'

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
    rawDescription = re.sub("[^\w]", " ", extracted.description.lower()).split()
    rawContent = re.sub("[^\w]", " ", pageContent.lower()).split()
    
    #rawDescriptionMinusPronouns = list(set(rawDescription) - set(pronouns))
    rawDescriptionMinusDiscard = [desWord for desWord in rawDescription if desWord not in discard]
    rawContentMinusDiscard = [contentWord for contentWord in rawContent if contentWord not in discard]
    
    # get the count of the the most common words
    descriptionWords = Counter(rawDescriptionMinusDiscard).most_common(10)
    contentWords = Counter(rawContentMinusDiscard).most_common(10)
    
    #print()
    print(descriptionWords)
    print(contentWords)
    
    cur.execute(sqlString, (url, sys.argv[1], extracted.title, extracted.description, extracted.image, pageContent, str(extracted.feeds), 1.0, titleSearchWordCount, 1))
    db.commit()
    #print(extracted)
    
    print("---------------------------------------------------")

  cur.close()