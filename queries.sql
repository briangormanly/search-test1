select word.word from word, resultWord where word.id = resultword.wordId and resultWord.wordScore > 10;
select word.word, resultPage.url, resultPage.title, resultword.wordScore, wordLocation.location from word, resultWord, resultPage, wordlocation where word.id = resultword.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and word.word = 'trump';
select search.searchPhrase, word.word, resultPage.url, resultPage.title, resultword.wordScore, wordLocation.location from word, resultWord, resultPage, search, wordlocation where word.id = resultword.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and search.id = 1 and resultWord.wordScore > 5;
select search.searchPhrase, word.word, resultPage.url, resultPage.title, resultword.wordScore, wordLocation.location from word, resultWord, resultPage, search, wordlocation where word.id = resultword.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and search.id = 16 and resultWord.wordScore > 5 order by wordScore desc;



select search.searchPhrase, word.word, resultPage.url, resultPage.title, resultword.wordScore, wordLocation.location from word, resultWord, resultPage, search, wordlocation where word.id = resultword.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and search.id = 16 and resultWord.wordScore > 5 order by wordScore desc;


select word.word, sum(resultword.wordScore) from word, resultWord, resultPage, search, wordlocation where word.id = resultword.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and search.id = 16 and resultWord.wordScore > 5 order by wordScore desc;

# get the next 10 words
select word.word, sum(resultword.wordScore) as score from word, resultWord, resultPage, search, wordlocation where word.id = resultword.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and search.id = 1 and resultWord.wordScore > 5 group by word.word order by score desc limit 10;


select word.word, sum(resultword.wordScore) as score from word, resultWord, resultPage, search, wordlocation where word.id = resultword.wordId and resultWord.resultPageId = resultPage.id and resultWord.wordLocationId = wordLocation.id and resultPage.searchId = search.id and (search.id = 52 || search.parentSearchId = 52) and resultWord.wordScore > 5 group by word.word order by score desc limit 100;