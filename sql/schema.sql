-- Schema modified: Tue April 27, 2021 @ 03:51:42 EDT
PRAGMA foreign_keys = ON;

CREATE TABLE users(
    userid VARCHAR(32) NOT NULL,
    summonerid VARCHAR(96) NOT NULL
);

CREATE TABLE lists(
    userid VARCHAR(32) NOT NULL,
    listname VARCHAR(64) NOT NULL,
    contents TEXT NOT NULL,
    PRIMARY KEY(userid, listname),
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE champs(
    champid INTEGER,
    userid VARCHAR(32) NOT NULL,
    mastery INTEGER,
    PRIMARY KEY(champid, userid),
    FOREIGN KEY(userid) REFERENCES users(userid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE sanity(
    champid INTEGER,
    userid VARCHAR(32) NOT NULL,
    sane BOOLEAN,
    feas INTEGER,
    PRIMARY KEY(champid, userid),
    FOREIGN KEY(userid) REFERENCES users(userid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE rotation(
    champid INTEGER,
    PRIMARY KEY(champid)
);
