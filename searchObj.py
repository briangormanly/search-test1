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
  
  searchId = 0
  searchString = ""
  parentSearchId = 0 
  searchStop = 5
  
  searchOpinion = 0.0
  
  #opinion words
  posWords = []
  negWords = []
  
  #opinion tracking for page
  opinion = 0.0
  pageOpinion = 0.0
  
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
    
    self.posWords = self.getAllPosWords()
    self.negWords = self.getAllNegWords()
    
    self.opinion = 0.0;
    self.pageOpinion = 0.0;
    
    #self.db = MySQLdb.connect(host="localhost",    # your host, usually localhost
    #    user="root",         # your username
    #    passwd="",  # your password
    #    db="google_test1")        # name of the data base
  
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    #self.cur = self.db.cursor()
  
  
  def saveResultPage(self, searchId, url, title, description, imageUrl, content, feeds, pageOpinionScore):
    sqlString = "insert into resultPage (searchId, url, title, description, imageUrl, content, feeds, pageOpinionScore) values (%s, %s, %s, %s, %s, %s, %s, %s);"
    
    with closing(self.db.cursor()) as cur:
    
      cur.execute(sqlString, (searchId, url, title, description, imageUrl, content, str(feeds), str(pageOpinionScore)))
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
  
  def updatePageOpinionScore(self, resultPageId):
    if resultPageId > 0:
      with closing(self.db.cursor()) as cur:
        sqlString = "update resultPage set pageOpinionScore= %s where id= %s;"
        cur.execute(sqlString, (self.pageOpinion, resultPageId))
        #pcur.execute(wordInsert, ([word]))
        self.db.commit()
        return cur.lastrowid;

  def updateSearchOpinionScore(self, searchId):
    if searchId > 0:

      self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)

      with closing(self.db.cursor()) as cur:
        sqlString = "update search set searchOpinionScore= %s where id= %s;"
        cur.execute(sqlString, (self.searchOpinion, searchId))
        #pcur.execute(wordInsert, ([word]))
        self.db.commit()
        return cur.lastrowid;

      self.db.close()
  
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
        
  def getAllPosWords(self):
    sqlString = "select opinionWord from opinionWord where isPositive=true;"
    
    # open db connection 
    self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)
    
    with closing(self.db.cursor()) as cur:
      res = cur.execute(sqlString, ())
      data = cur.fetchall()
      posWords = []
      for row in data:
          posWords.append(row[0])
      
      return posWords
    
    #close db connection
    self.db.close()
        
  def getAllNegWords(self):
    sqlString = "select opinionWord from opinionWord where isPositive=false;"
    
    # open db connection 
    self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)
    
    with closing(self.db.cursor()) as cur:
      res = cur.execute(sqlString, ())
      data = cur.fetchall()
      negWords = []
      for row in data:
          negWords.append(row[0])
      
      return negWords
    
    #close db connection
    self.db.close()
    
  def checkOpinionOnWord(self, word, wordLocationFactor):
     
    #see if word is positive / negative
    if(word in self.posWords):
      self.pageOpinion += (.01 * wordLocationFactor)
      
    elif(word in self.negWords):
      self.pageOpinion -= (.01 * wordLocationFactor)
    
  #Reports
  def searchOpinionResults(self):
    
    # open db connection 
    #self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)
    
    with closing(self.db.cursor()) as cur:
      
      sqlString = "select resultPage.id, search.id as SearchId, resultPage.url, resultPage.pageOpinionScore from resultPage, search where search.id = resultPage.searchId and (search.id = %s or search.parentSearchId = %s);"
      print("select resultPage.id, search.id as SearchId, resultPage.url, resultPage.pageOpinionScore from resultPage, search where search.id = resultPage.searchId and (search.id =  or search.parentSearchId = )")
      res = cur.execute(sqlString, (self.searchId, self.searchId))
      data = cur.fetchall()
      print("results: ")
      print(self.searchId)
      print(data)
      
      for row in data:
        #total up the sentiment for the whole search
        print(row[3])
        #self.searchOpinion += float(row[3])
        
        print("url: " + row[2] + " opinion: " + str(row[3]))
    
    print("Search " + self.searchString + " total Opinion: " + str(self.searchOpinion))
    
    #close db connection
    #self.db.close()
      
  
  def asyncSearch(self):
    threading.Thread(target=self.doSearch).start()
          
  def doSearch(self):
    
    # open db connection 
    self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)
    
    # Save the search string
    self.searchId = self.saveSearch()
      
    #print(searchString)
    print("search string is: ")
    print(self.searchString)
    
    for url in search(self.searchString, stop=self.searchStop):
      print("url is ")
      print(url)
      html = requests.get(url).text
      extracted = extraction.Extractor().extract(html, source_url=url)
      
      #reset opinion for new page
      self.pageOpinion = 0.0
    
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
        rawTitleMinusDiscard += [desWord for desWord in rawTitle if desWord < 9999999999]
        rawDescriptionMinusDiscard = [desWord for desWord in rawDescription if desWord not in self.discard]
        rawDescriptionMinusDiscard += [desWord for desWord in rawDescription if desWord < 9999999999]
        rawContentMinusDiscard = [contentWord for contentWord in rawContent if contentWord not in self.discard]
        rawContentMinusDiscard += [contentWord for contentWord in rawContent if contentWord < 9999999999]
    
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
        currentResultPageId = self.saveResultPage(self.searchId, url, ','.join(rawTitle), ','.join(rawDescription), extracted.image, pageContent, str(extracted.feeds), self.pageOpinion)
    
        #word breakdown
        for word in self.searchString:
          if word in url.lower() and len(word) > 1:
            #check to see the word exists and get id
            currentWordId = saveWord(word, db, cur)
            #print(wordId)
            self.saveResultWord(currentResultPageId, currentWordId, 6, self.getWordLocation("url"), True)
            
            #update opinion
            checkOpinionOnWord(word, 6)
    
        for word in rawTitleMinusDiscard:
          if len(word) > 1:
            currentWordId = self.saveWord(word)
            if word in self.searchString:
              self.saveResultWord(currentResultPageId, currentWordId, 4, self.getWordLocation("title"), True)
              
              #update opinion
              self.checkOpinionOnWord(word, 4)
            else:
              self.saveResultWord(currentResultPageId, currentWordId, 2, self.getWordLocation("title"), False)
              
              #update opinion
              self.checkOpinionOnWord(word, 2)
    
        for word in rawDescriptionMinusDiscard:
          if len(word) > 1:
            currentWordId = self.saveWord(word)
            if word in self.searchString:
              self.saveResultWord(currentResultPageId, currentWordId, 3, self.getWordLocation("description"), True)
              
              #update opinion
              self.checkOpinionOnWord(word, 3)
            else:
              self.saveResultWord(currentResultPageId, currentWordId, 1, self.getWordLocation("description"), False)
              
              #update opinion
              self.checkOpinionOnWord(word, 1)

        for word in rawContentMinusDiscard:
          if len(word) > 1:
            currentWordId = self.saveWord(word)
            if word in self.searchString:
              self.saveResultWord(currentResultPageId, currentWordId, 3, self.getWordLocation("content"), True)
              
              #update opinion
              self.checkOpinionOnWord(word, 3)
            elif word in significantContentWords:
              self.saveResultWord(currentResultPageId, currentWordId, 2, self.getWordLocation("content"), False)
              
              #update opinion
              self.checkOpinionOnWord(word, 2)
            else:
              self.saveResultWord(currentResultPageId, currentWordId, 1, self.getWordLocation("content"), False)
              
              #update opinion
              self.checkOpinionOnWord(word, 1)
          
        #update the opinion scrore
        self.updatePageOpinionScore(currentResultPageId)
        
        #update the running searchOpinion score for the whole search
        self.searchOpinion += self.pageOpinion
        
    # get the opinion results for this search
    self.searchOpinionResults()
        
    #this is where i should save the search opinion!!!!! (and add up the total opinion from all the page ones)
    self.updateSearchOpinionScore(self.searchId)
    
    #close db connection
    self.db.close()
    
    return self.searchId

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
