create database google_test1 character set utf8;
use google_test1;
create table searchResults (id bigint primary key auto_increment, search varchar(200), url varchar(300), title varchar(300), description TEXT, imageUrl varchar(300), content LONGTEXT, head TEXT, scrapeTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updateTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, rating double);
