-- Schema modified: Tue April 27, 2021 @ 07:18:00 EDT
PRAGMA foreign_keys = ON;

CREATE TABLE users(
    userid VARCHAR(32) NOT NULL,
    summonerid VARCHAR(96) NOT NULL
);

CREATE TABLE lists(
    userid VARCHAR(32) NOT NULL,
    listname VARCHAR(64) NOT NULL,
    PRIMARY KEY(userid, listname),
    FOREIGN KEY(userid) REFERENCES users(userid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE listdata(
    userid VARCHAR(32) NOT NULL,
    listname VARCHAR(64) NOT NULL,
    champid INTEGER,
    PRIMARY KEY(userid, listname, champid),
    FOREIGN KEY(userid, listname) REFERENCES lists(userid, listname)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE champs(
    champid INTEGER,
    userid VARCHAR(32) NOT NULL,
    mastery INTEGER,
    owned BOOLEAN,
    displayname VARCHAR(32) NOT NULL,
    PRIMARY KEY(champid, userid),
    FOREIGN KEY(userid) REFERENCES users(userid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE sanity(
    champid INTEGER,
    userid VARCHAR(32) NOT NULL,
    position VARCHAR(10) NOT NULL,
    sane BOOLEAN,
    feas INTEGER,
    PRIMARY KEY(champid, userid, position),
    FOREIGN KEY(userid) REFERENCES users(userid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE rotation(
    champid INTEGER,
    PRIMARY KEY(champid)
);

CREATE TABLE preferences(
    userid VARCHAR(32) NOT NULL,
    select_owned BOOLEAN,
    never_recommend TEXT,
    PRIMARY KEY(userid),
    FOREIGN KEY(userid) REFERENCES users(userid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE aliases(
    champid INTEGER,
    userid VARCHAR(32) NOT NULL,
    alias VARCHAR(64) NOT NULL,
    PRIMARY KEY(champid, userid, alias),
    FOREIGN KEY(champid, userid) REFERENCES champs(champid, userid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
