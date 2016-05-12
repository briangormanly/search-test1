create database google_test1 character set utf8;
use google_test1;
create table search (id bigint primary key auto_increment, searchPhrase varchar(200), parentSearchId bigint, searchTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
create table word (id bigint primary key auto_increment, word varchar(150), createTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updateTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP);
create table resultPage (id bigint primary key auto_increment, searchId bigint, url varchar(300), title varchar(300), description TEXT, imageUrl varchar(300), content LONGTEXT, feeds TEXT, createTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updateTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP);
create table resultWord (id bigint primary key auto_increment, resultPageId bigint, wordId bigint, urlWordCount int, titleWordCount int, descriptionWordCount int, contentWordCount int, isSearchWord boolean); 


#create table searchResults (id bigint primary key auto_increment, search varchar(200), url varchar(300), title varchar(300), description TEXT, imageUrl varchar(300), content LONGTEXT, feeds TEXT, searchWordCount int, friendword varchar(100), friendwordCount int, scrapeTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updateTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, rating double);