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
    passwd="test",  # your password
    db="google_test1")        # name of the data base
  
# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

def saveResultPage(searchId, url, title, description, imageUrl, content, feeds):
  sqlString = "insert into resultPage (searchId, url, title, description, imageUrl, content, feeds) values (%s, %s, %s, %s, %s, %s, %s);"
  cur.execute(sqlString, (searchId, url, title, description, imageUrl, content, str(feeds)))
  #cur.execute(wordInsert, ([word]))
  db.commit()
  return cur.lastrowid;

def saveResultWord(resultPageId, wordId, wordScore, wordLocationId, isSearchWord):
  #check to see if this result word exists for this searchResult and word
  resultWordId = getUniqueWordResult(wordId, resultPageId, wordLocationId)
  if resultWordId is not -1:
    #get the current score for existing resultWord
    sqlString = "select wordScore from resultWord where resultPageId= %s and wordId= %s and wordLocationId = %s;"
    cur.execute(sqlString, (resultPageId, wordId, wordLocationId))
    data = cur.fetchall()
    if data:
      newCount = data[0][0] + wordScore
      
      sqlString = "update resultWord set wordScore= %s where resultPageId= %s and wordId= %s and wordLocationId = %s;"
      cur.execute(sqlString, (newCount, resultPageId, wordId, wordLocationId))
      #pcur.execute(wordInsert, ([word]))
      db.commit()
      return cur.lastrowid;
    
  else:
    sqlString = "insert into resultWord (resultPageId, wordId, wordScore, wordLocationId, isSearchWord) values (%s, %s, %s, %s, %s);"
    cur.execute(sqlString, (resultPageId, wordId, wordScore, wordLocationId, isSearchWord))
    #pcur.execute(wordInsert, ([word]))
    db.commit()
    return cur.lastrowid;
  
def saveWord(word):
  existingWord = getWord(word)
  #print existingWord
  if existingWord is -1:
    #create the word
    #print("1 bye");
    wordInsert = "insert into word (word) values (%s);"
    cur.execute(wordInsert, ([word]))
    db.commit()
    #print("2 bye")
    #print db.insert_id()
    return cur.lastrowid;
  else:
    return existingWord

def saveSearch(searchPhrase, parentId):
  sqlString = "insert into search (searchPhrase, parentSearchId) values (%s, %s);"
  cur.execute(sqlString, (str(searchPhrase), parentId))
  db.commit()
  return cur.lastrowid;

def getWord(word):
  sqlString = "select * from word where word= %s;"
  res = cur.execute(sqlString, ([word]))
  data = cur.fetchall()
  if data:
    return data[0][0]
  else:
    return -1

def getWordLocation(wordLocation):
  sqlString = "select * from wordLocation where location= %s;"
  res = cur.execute(sqlString, ([wordLocation]))
  data = cur.fetchall()
  if data:
    return data[0][0]
  else:
    return -1

def getUniqueWordResult(wordId, resultPageId, wordLocationId):
  sqlString = "select * from resultWord where wordId= %s and resultPageId= %s and wordLocationId= %s;"
  res = cur.execute(sqlString, (wordId, resultPageId, wordLocationId))
  data = cur.fetchall()
  if data:
    return data[0][0]
  else:
    return -1

def doSearch(searchString, level, searchStop):
  # Save the search string
  currentSearchId = saveSearch(searchPhrase, level)
  
  #print(searchString)
  for url in search(searchString, stop=searchStop):
    
    html = requests.get(url).text
    extracted = extraction.Extractor().extract(html, source_url=url)
    
    if extracted is not None:
      page_text = html.encode('utf-8').decode('ascii', 'ignore')
      soup = BeautifulSoup.BeautifulSoup(page_text)
      pageContent = "";
      for node in soup.findAll('p'):
        pageContent+=''.join(node.findAll(text=True))
    
      #count all the words in the text to find friendly words
      rawTitle = []
      if extracted.title is not None:
        rawTitle = re.sub("[^\w]", " ", extracted.title.lower()).split()
      
      rawDescription = []
      if extracted.description is not None:
        rawDescription = re.sub("[^\w]", " ", extracted.description.lower()).split()
      
      rawContent = re.sub("[^\w]", " ", pageContent.lower()).split()
    
      rawTitleMinusDiscard = [desWord for desWord in rawTitle if desWord not in discard]
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
      
      #print(significantNumber)
      for cWord in contentWords:
        if(cWord[1] > significantNumber):
          significantContentWords+=cWord
        #print(cWord[1])
    
      #save this page
      currentResultPageId = saveResultPage(currentSearchId, url, ','.join(rawTitle), ','.join(rawDescription), extracted.image, pageContent, str(extracted.feeds))
    
      #word breakdown
      for word in searchPhrase:
        if word in url.lower() and len(word) > 1:
          #check to see the word exists and get id
          currentWordId = saveWord(word)
          #print(wordId)
          saveResultWord(currentResultPageId, currentWordId, 6, getWordLocation("url"), True)
    
      for word in rawTitleMinusDiscard:
        if len(word) > 1:
          currentWordId = saveWord(word)
          if word in searchPhrase:
            saveResultWord(currentResultPageId, currentWordId, 4, getWordLocation("title"), True)
          else:
            saveResultWord(currentResultPageId, currentWordId, 2, getWordLocation("title"), False)
    
      for word in rawDescriptionMinusDiscard:
        if len(word) > 1:
          currentWordId = saveWord(word)
          if word in searchPhrase:
            saveResultWord(currentResultPageId, currentWordId, 3, getWordLocation("description"), True)
          else:
            saveResultWord(currentResultPageId, currentWordId, 1, getWordLocation("description"), False)

      for word in rawContentMinusDiscard:
        if len(word) > 1:
          currentWordId = saveWord(word)
          if word in searchPhrase:
            saveResultWord(currentResultPageId, currentWordId, 3, getWordLocation("content"), True)
          elif word in significantContentWords:
            saveResultWord(currentResultPageId, currentWordId, 2, getWordLocation("content"), False)
          else:
            saveResultWord(currentResultPageId, currentWordId, 1, getWordLocation("content"), False)
  
  return currentSearchId

def getNextLevelSearches(searchId):
  # get the most common words for the previous search
  #
  sqlString = "select word.word, sum(resultWord.wordScore) as score from word, resultWord, resultPage, search, wordLocation where word.id = resultWord.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and search.id = %s and resultWord.wordScore > 10 group by word.word order by score desc limit 10;"
  cur.execute(sqlString, ([searchId]))
  data = cur.fetchall()
  if data:
    return data
  else:
    return -1
  

# words we don't care about
discard = '[39, a, all, also, another, and, any, anybody, anyone, anything, are, be, both, by, com, each, either, everybody, everyone, everything, few, for, get, has, he, her, hers, herself, him, himself, his, http, https, i, it, its, itself, little, many, me, middot, mine, more, most, much, my, myself, nbsp, neither, nobody, none, nothing, of, one, other, others, our, ours, ourselves, several, she, some, somebody, someone, something, that,their, theirs, them, themselves, these, the, they, this, those, to, us, was, we, what, whatever, which, whichever, while, will, who, whoever, whom, whomever, whose, with, www, you, your, yours, yourself, yourselves]'

if(len(sys.argv) > 1):
  
  # get the user entered search phrase
  searchPhrase = [];
  for phrasePart in sys.argv[1:len(sys.argv)]:
    searchPhrase.append(phrasePart)
    
  #print(searchPhrase)
  
  #searchString = str(searchPhrase).strip('[]').strip('\'')
  searchString = ' '.join(map(str, searchPhrase))
  
  searchId = doSearch(searchString, 0, 5)
  newSearchWords = getNextLevelSearches(searchId)
  print(newSearchWords)
  for searchWord in newSearchWords:
    newSearchPhrase = searchString + " " + searchWord[0]
    print("starting search:::")
    print(newSearchPhrase)
    doSearch(newSearchPhrase, searchId, 5)
  
  
  
        
        #save the result word
        #saveResultWord(currentResultPageId, currentWordId, wordCount, titleWordCount, descriptionWordCount, contentWordCount)

    
            
      #count the occurances of the search word in the site and weighted total (url = n*5, title = v*3, description v*2, content = v*1)
      #urlSearchWordCount=0
      #for word in searchPhrase:
      #  if word in url.lower():
      #    #check to see the word exists and get id
      #    wordId = saveWord(word)
      #    #print(wordId)
      #    urlSearchWordCount+=5
      #    saveResultPage(currentSearchId,)
    
      #titleSearchWordCount=0
      #for word in searchPhrase:
      #  if word in extracted.title.lower():
      #    titleSearchWordCount+=3
        
      #descriptionSearchWordCount=0
      #for word in searchPhrase:
      #  if word in extracted.description.lower():
      #    descriptionSearchWordCount+=2
        
      #ContentSearchWordCount=0
      #for word in searchPhrase:
      #  if word in pageContent.lower():
      #    ContentSearchWordCount+=1
    
      #print(urlSearchWordCount)
      #print(titleSearchWordCount)
      #print(descriptionSearchWordCount)
      #print(ContentSearchWordCount)
    
      #titleSearchWordCount+=extracted.title.lower().count(searchPhrase.lower()) *3
      #titleSearchWordCount+=extracted.description.lower().count(searchPhrase.lower()) *2
      #titleSearchWordCount+=pageContent.lower().count(searchPhrase.lower())
    
    
    
      #print()
      #print(descriptionWords)
      #print(significantContentWords)
    
      #
      # SQL
      #
    
      #sqlString = "insert into searchResults (url, search, title, description, imageUrl, content, feeds, rating, searchWordCount, friendwordCount) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    
      #cur.execute(sqlString, (url, searchPhrase, extracted.title, extracted.description, extracted.image, pageContent, str(extracted.feeds), 1.0, titleSearchWordCount, 1))
      #db.commit()
      #print(extracted)

  cur.close()