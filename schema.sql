DROP TABLE IF EXISTS list;
DROP TABLE IF EXISTS trailer;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS production_countries;
DROP TABLE IF EXISTS spoken_languages;
CREATE TABLE genre(
   genre_id INTEGER  PRIMARY KEY 
  ,name     VARCHAR(100) NOT NULL
);


CREATE TABLE production_countries(
   production_id VARCHAR(2) PRIMARY KEY
  ,country_name          VARCHAR(32) NOT NULL
);


CREATE TABLE spoken_languages(
   spoken_id     VARCHAR(2) PRIMARY KEY
  ,language_name VARCHAR(23) NOT NULL
);

CREATE TABLE users(
   username VARCHAR(100) PRIMARY KEY
  ,email    VARCHAR(100) NOT NULL
);



CREATE TABLE movies(
   adult                BOOLEAN  
  ,genre_id             INTEGER NOT NULL references genre(genre_id)
        ,movie_id             INTEGER  PRIMARY KEY
  ,original_language    VARCHAR(2) 
  ,popularity           NUMERIC(8,3) 
  ,production_id VARCHAR(2) NOT NULL references production_countries(production_id)

  ,release_date         DATE  
  ,runtime              INTEGER  
,spoken_id     VARCHAR(2) NOT NULL references spoken_languages(spoken_id)
  ,movie_status               VARCHAR(15) 
  ,title                VARCHAR(9999) 
  

);

CREATE TABLE trailer(
   Video_ID  VARCHAR(100) PRIMARY KEY
  ,movie_id  INT  NOT NULL references Movies(movie_id)
  ,Title     VARCHAR(100)
  ,trailer_length    VARCHAR(7)
  ,Published DATE 
  ,Views     INTEGER 
  ,Likes     INTEGER 
  ,Comments  INTEGER 
--   ,movie_id FOREIGN KEY references Movies(movie_id)
);

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews(
   review_id VARCHAR(100) NOT NULL PRIMARY KEY
  ,username  VARCHAR(100) NOT NULL references Users(username)
  ,movie_id  INTEGER  NOT NULL references Movies(movie_id)
  ,review    VARCHAR(9999) NOT NULL
    
);


CREATE TABLE list(
   list_id        SERIAL  PRIMARY KEY
  ,list_name      VARCHAR(100)
  ,movie_id      INTEGER references Movies(movie_id)
  ,favorite_count INTEGER  DEFAULT 0
  ,created_by     VARCHAR(100) NOT NULL references Users(username)
 
  
);
