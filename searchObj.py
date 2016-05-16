from google import search
from google import get_page
from collections import Counter
from contextlib import closing
import re
import sys
import MySQLdb
import extraction
import requests
import BeautifulSoup
import thread
import threading

class SearchObj(object):
  dbHost = "localhost"
  dbUser = "root"
  dbPassword = ""
  dbName = "google_test1"
  
  searchString = ""
  parentSearchId = 0 
  searchStop = 5
  
  db = 0;
  #cur = 0;
  
  # words we don't care about
  discard = '[39, a, all, also, amp, another, and, any, anybody, anyone, anything, are, be, both, but, by, com, each, either, everybody, everyone, everything, few, for, from, get, has, have, he, her, hers, herself, him, himself, his, http, https, i, if, it, its, itself, little, many, me, middot, mine, more, most, much, my, myself, nbsp, neither, nobody, none, nothing, of, one, other, others, our, ours, ourselves, several, she, some, somebody, someone, something, than, that, their, theirs, them, themselves, then, these, the, they, this, those, to, us, was, we, what, whatever, which, whichever, while, will, who, whoever, whom, whomever, whose, with, www, you, your, yours, yourself, yourselves]'
  
  def __init__(self, searchString, parentSearchId, searchStop):
    self.searchString = searchString
    self.parentSearchId = parentSearchId
    self.searchStop = searchStop  
    
    self.dbUser = "root"
    self.dbPassword = ""
    self.dbName = "google_test1"
    
    #self.db = MySQLdb.connect(host="localhost",    # your host, usually localhost
    #    user="root",         # your username
    #    passwd="",  # your password
    #    db="google_test1")        # name of the data base
  
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    #self.cur = self.db.cursor()
  
  
  def saveResultPage(self, searchId, url, title, description, imageUrl, content, feeds):
    sqlString = "insert into resultPage (searchId, url, title, description, imageUrl, content, feeds) values (%s, %s, %s, %s, %s, %s, %s);"
    
    with closing(self.db.cursor()) as cur:
    
      cur.execute(sqlString, (searchId, url, title, description, imageUrl, content, str(feeds)))
      #cur.execute(wordInsert, ([word]))
      self.db.commit()
      return cur.lastrowid;

  def saveResultWord(self, resultPageId, wordId, wordScore, wordLocationId, isSearchWord):
    #check to see if this result word exists for this searchResult and word
    resultWordId = self.getUniqueWordResult(wordId, resultPageId, wordLocationId)
    if resultWordId is not -1:
      #get the current score for existing resultWord
      sqlString = "select wordScore from resultWord where resultPageId= %s and wordId= %s and wordLocationId = %s;"
      
      with closing(self.db.cursor()) as cur:
        cur.execute(sqlString, (resultPageId, wordId, wordLocationId))
        data = cur.fetchall()
        if data:
          newCount = data[0][0] + wordScore
          
          sqlString = "update resultWord set wordScore= %s where resultPageId= %s and wordId= %s and wordLocationId = %s;"
          cur.execute(sqlString, (newCount, resultPageId, wordId, wordLocationId))
          #pcur.execute(wordInsert, ([word]))
          self.db.commit()
          return cur.lastrowid;
          
    else:
      sqlString = "insert into resultWord (resultPageId, wordId, wordScore, wordLocationId, isSearchWord) values (%s, %s, %s, %s, %s);"
      
      with closing(self.db.cursor()) as cur:
        cur.execute(sqlString, (resultPageId, wordId, wordScore, wordLocationId, isSearchWord))
        #pcur.execute(wordInsert, ([word]))
        self.db.commit()
        return cur.lastrowid;
  
  def saveWord(self, word):
    existingWord = self.getWord(word)
    #print existingWord
    if existingWord is -1:
      #create the word
      #print("1 bye");
      wordInsert = "insert into word (word) values (%s);"
      
      with closing(self.db.cursor()) as cur:
        cur.execute(wordInsert, ([word]))
        self.db.commit()
        #print("2 bye")
        #print db.insert_id()
        return cur.lastrowid;
    else:
      return existingWord

  def saveSearch(self):
    sqlString = "insert into search (searchPhrase, parentSearchId) values (%s, %s);"
    with closing(self.db.cursor()) as cur:
      cur.execute(sqlString, (str(self.searchString), self.parentSearchId))
      self.db.commit()
      return cur.lastrowid;

  def getWord(self, word):
    sqlString = "select * from word where word= %s;"
    
    with closing(self.db.cursor()) as cur:
      res = cur.execute(sqlString, ([word]))
      data = cur.fetchall()
      if data:
        return data[0][0]
      else:
        return -1

  def getWordLocation(self, wordLocation):
    sqlString = "select * from wordLocation where location= %s;"
    
    with closing(self.db.cursor()) as cur:
      res = cur.execute(sqlString, ([wordLocation]))
      data = cur.fetchall()
      if data:
        return data[0][0]
      else:
        return -1

  def getUniqueWordResult(self, wordId, resultPageId, wordLocationId):
    sqlString = "select * from resultWord where wordId= %s and resultPageId= %s and wordLocationId= %s;"
    
    with closing(self.db.cursor()) as cur:
      res = cur.execute(sqlString, (wordId, resultPageId, wordLocationId))
      data = cur.fetchall()
      if data:
        return data[0][0]
      else:
        return -1
  
  def asyncSearch(self):
    threading.Thread(target=self.doSearch).start()
          
  def doSearch(self):
    
    # open db connection 
    self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)
    
    # Save the search string
    currentSearchId = self.saveSearch()
      
    #print(searchString)
    print("search string is: ")
    print(self.searchString)
    #urls = search(self.searchString, stop=self.searchStop)
    print("urls:::::::::::::::: ")
    #print(list(urls))
    #print("url try 1")
    #print(url[0])
    #for url in urls:
    for url in search(self.searchString, stop=self.searchStop):
      print("url is ")
      print(url)
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
    
        rawTitleMinusDiscard = [desWord for desWord in rawTitle if desWord not in self.discard]
        rawDescriptionMinusDiscard = [desWord for desWord in rawDescription if desWord not in self.discard]
        rawContentMinusDiscard = [contentWord for contentWord in rawContent if contentWord not in self.discard]
    
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
        currentResultPageId = self.saveResultPage(currentSearchId, url, ','.join(rawTitle), ','.join(rawDescription), extracted.image, pageContent, str(extracted.feeds))
    
        #word breakdown
        for word in self.searchString:
          if word in url.lower() and len(word) > 1:
            #check to see the word exists and get id
            currentWordId = saveWord(word, db, cur)
            #print(wordId)
            self.saveResultWord(currentResultPageId, currentWordId, 6, self.getWordLocation("url"), True)
    
        for word in rawTitleMinusDiscard:
          if len(word) > 1:
            currentWordId = self.saveWord(word)
            if word in self.searchString:
              self.saveResultWord(currentResultPageId, currentWordId, 4, self.getWordLocation("title"), True)
            else:
              self.saveResultWord(currentResultPageId, currentWordId, 2, self.getWordLocation("title"), False)
    
        for word in rawDescriptionMinusDiscard:
          if len(word) > 1:
            currentWordId = self.saveWord(word)
            if word in self.searchString:
              self.saveResultWord(currentResultPageId, currentWordId, 3, self.getWordLocation("description"), True)
            else:
              self.saveResultWord(currentResultPageId, currentWordId, 1, self.getWordLocation("description"), False)

        for word in rawContentMinusDiscard:
          if len(word) > 1:
            currentWordId = self.saveWord(word)
            if word in self.searchString:
              self.saveResultWord(currentResultPageId, currentWordId, 3, self.getWordLocation("content"), True)
            elif word in significantContentWords:
              self.saveResultWord(currentResultPageId, currentWordId, 2, self.getWordLocation("content"), False)
            else:
              self.saveResultWord(currentResultPageId, currentWordId, 1, self.getWordLocation("content"), False)
    
    
    #close db connection
    self.db.close()
    
    return currentSearchId

  def getNextLevelSearches(self, searchId):
    # get the most common words for the previous search
    #
    
    # open db connection 
    self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)
    
    sqlString = "select word.word, sum(resultWord.wordScore) as score from word, resultWord, resultPage, search, wordLocation where word.id = resultWord.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and search.id = %s and resultWord.wordScore > 10 group by word.word order by score desc limit 10;"
    
    data = "-1"
    with closing(self.db.cursor()) as cur:
      cur.execute(sqlString, ([searchId]))
      data = cur.fetchall()
      
    #close db connection
    self.db.close()
    
    return data
