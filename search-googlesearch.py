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

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
    user="root",         # your username
    passwd="",  # your password
    db="google_test1")        # name of the data base
  
# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

def checkWord(word):
  # see if the word is in the word table
  print(word)
  searchSqlString = "select id from word where word=%s);"
  cur.execute(searchSqlString, (word))
  print("please")
  if cur.fetchone()[0]:
    #return the wordId
    print("hi")
    print cur.fetchone()[0]
    return cur.fetchone()[0];
  else:
    #create the word
    print("1 bye");
    searchSqlString = "insert into word (word) values (%s);"
    cur.execute(searchSqlString, (word))
    print("2 bye")
    print db.insert_id()
    return db.insert_id();


# words we don't care about
discard = '[a, all, also, another, and, any, anybody, anyone, anything, are, be, both, by, each, either, everybody, everyone, everything, few, for, get, has, he, her, hers, herself, him, himself, his, i, it, its, itself, little, many, me, mine, more, most, much, my, myself, nbsp, neither, nobody, none, nothing, of, one, other, others, our, ours, ourselves, several, she, some, somebody, someone, something, that,their, theirs, them, themselves, these, the, they, this, those, to, us, was, we, what, whatever, which, whichever, while, will, who, whoever, whom, whomever, whose, with, you, your, yours, yourself, yourselves]'

if(len(sys.argv) > 1):
  
  # get the user entered search phrase
  searchPhrase = [];
  for phrasePart in sys.argv[1:len(sys.argv)]:
    searchPhrase.append(phrasePart)
    
  print(searchPhrase)
  
  #searchString = str(searchPhrase).strip('[]').strip('\'')
  searchString = ' '.join(map(str, searchPhrase))
  
  # Save the search string
  searchSqlString = "insert into search (searchPhrase, parentSearchId) values (%s, %s);"
  cur.execute(searchSqlString, (str(searchPhrase), 0))
  db.commit()
  
  print(searchString)
  for url in search(searchString, stop=8):
    print(url)
    #print ("hi")
    html = requests.get(url).text
    extracted = extraction.Extractor().extract(html, source_url=url)
    #print extracted.title, extracted.description, extracted.image, extracted.url
    
    soup = BeautifulSoup.BeautifulSoup(html)
    pageContent = "";
    for node in soup.findAll('p'):
      pageContent+=''.join(node.findAll(text=True))
      
    
    #count the occurances of the search word in the site and weighted total (url = n*5, title = v*3, description v*2, content = v*1)
    urlSearchWordCount=0
    for word in searchPhrase:
      if word in url.lower():
        #check to see the word exists and get id
        wordId = checkWord(word)
        print(wordId)
        urlSearchWordCount+=5
    
    titleSearchWordCount=0
    for word in searchPhrase:
      if word in extracted.title.lower():
        titleSearchWordCount+=3
        
    descriptionSearchWordCount=0
    for word in searchPhrase:
      if word in extracted.description.lower():
        descriptionSearchWordCount+=2
        
    ContentSearchWordCount=0
    for word in searchPhrase:
      if word in pageContent.lower():
        ContentSearchWordCount+=1
    
    print(urlSearchWordCount)
    print(titleSearchWordCount)
    print(descriptionSearchWordCount)
    print(ContentSearchWordCount)
    
    #titleSearchWordCount+=extracted.title.lower().count(searchPhrase.lower()) *3
    #titleSearchWordCount+=extracted.description.lower().count(searchPhrase.lower()) *2
    #titleSearchWordCount+=pageContent.lower().count(searchPhrase.lower())
    
    #count all the words in the text to find friendly words
    rawDescription = re.sub("[^\w]", " ", extracted.description.lower()).split()
    rawContent = re.sub("[^\w]", " ", pageContent.lower()).split()
    
    #rawDescriptionMinusPronouns = list(set(rawDescription) - set(pronouns))
    rawDescriptionMinusDiscard = [desWord for desWord in rawDescription if desWord not in discard]
    rawContentMinusDiscard = [contentWord for contentWord in rawContent if contentWord not in discard]
    
    # get the count of the the most common words
    descriptionWords = Counter(rawDescriptionMinusDiscard).most_common()
    contentWords = Counter(rawContentMinusDiscard).most_common()
    
    # only returns words with a signifigant occurance
    #print(len(rawContentMinusDiscard))
    significantContentWords = []; 
    significantNumber = len(rawContentMinusDiscard)/200
    
    if significantNumber == 0:
      significantNumber = 1
      
    print(significantNumber)
    for cWord in contentWords:
      if(cWord[1] > significantNumber):
        significantContentWords+=cWord
      #print(cWord[1])
    
    #print()
    #print(descriptionWords)
    #print(significantContentWords)
    
    #
    # SQL
    #
    
    sqlString = "insert into searchResults (url, search, title, description, imageUrl, content, feeds, rating, searchWordCount, friendwordCount) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    
    cur.execute(sqlString, (url, searchPhrase, extracted.title, extracted.description, extracted.image, pageContent, str(extracted.feeds), 1.0, titleSearchWordCount, 1))
    db.commit()
    #print(extracted)
    
    print("---------------------------------------------------")

  cur.close()