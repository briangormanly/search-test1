#!/usr/bin/python
from google import search
from google import get_page
from collections import Counter
from searchObj import SearchObj
import re
import sys
import MySQLdb
import extraction
import requests
import BeautifulSoup
import thread


if(len(sys.argv) > 1):
  
  # get the user entered search phrase
  searchPhrase = [];
  
  # search words used
  
  
  for phrasePart in sys.argv[1:len(sys.argv)]:
    searchPhrase.append(phrasePart)
    
  #print(searchPhrase)
  
  #searchString = str(searchPhrase).strip('[]').strip('\'')
  searchString = ' '.join(map(str, searchPhrase))
  
  # create the first searchObj
  searchOne = SearchObj(searchString, 0, 5)
  print("about to search!")
  searchId = searchOne.doSearch()
  newSearchWords = searchOne.getNextLevelSearches(searchId)
  print("new search terms!!!")
  print(newSearchWords)
  #searchId = doSearch(searchString, 0, 5)
  #newSearchWords = getNextLevelSearches(searchId)
  
  
  print(newSearchWords)
  for searchWord in newSearchWords:
    
    # check to see if this is a repeat search
    if searchWord[0] not in searchPhrase:
      newSearchPhrase = searchString + " " + searchWord[0]
      print("new search phrase:::")
      print(newSearchPhrase)
      print("new search parant id")
      print(searchId)
      
      # create searchObj for this sub search
      subSearch = SearchObj(newSearchPhrase, searchId, 5)
      print("looking in new object for searchString")
      print(subSearch.searchString)
      #thread.start_new_thread(subSearch.doSearch, ())
      subSearch.asyncSearch()
      
      #newSubSearchWords = subSearch.getNextLevelSearches(searchId)
      #print("sub search search completed")
      #print(newSearchPhrase)
      #print("sub search new search words")
      #print(newSubSearchWords)
      
    else:
      print("dup!!!")
      print(searchWord)
      
  
    
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