CREATE TABLE comments
      (ID INTEGER PRIMARY KEY   AUTOINCREMENT,
       USER_ID        INT    NOT NULL,
       COMMENT        TEXT     NOT NULL);
CREATE TABLE users
      (ID INTEGER PRIMARY KEY   AUTOINCREMENT,
       FIRST_NAME     TEXT    NOT NULL,
       LAST_NAME        TEXT     NOT NULL,
       MIDDLE_NAME      TEXT,
       CITY_ID INTEGER,
       TELEPHON TEXT,
       EMAIL TEXT);
CREATE TABLE citys
      (ID INTEGER PRIMARY KEY   AUTOINCREMENT,
       REGION_ID        INT    NOT NULL,
       CITY        TEXT     NOT NULL);
CREATE TABLE regions
      (ID INTEGER PRIMARY KEY   AUTOINCREMENT,
       REGION        TEXT     NOT NULL);
INSERT INTO regions (REGION) VALUES ('Краснодарский край');
INSERT INTO regions (REGION) VALUES ('Ростовская область');
INSERT INTO regions (REGION) VALUES ('Ставропольский край');
INSERT INTO citys (REGION_ID,CITY) VALUES (1,'Краснодар');
INSERT INTO citys (REGION_ID,CITY) VALUES (1,'Кропоткин');
INSERT INTO citys (REGION_ID,CITY) VALUES (1,'Славянск');
INSERT INTO citys (REGION_ID,CITY) VALUES (2,'Ростов');
INSERT INTO citys (REGION_ID,CITY) VALUES (2,'Шахты');
INSERT INTO citys (REGION_ID,CITY) VALUES (2,'Батайск');
INSERT INTO citys (REGION_ID,CITY) VALUES (3,'Ставрополь');
INSERT INTO citys (REGION_ID,CITY) VALUES (3,'Пятигорск');
INSERT INTO citys (REGION_ID,CITY) VALUES (3,'Кисловодск');