/******************************************************************************/
/* General tables                                                             */
/******************************************************************************/

/*
 * Create USERS table with indizes on ID (PK) and Name
 */
CREATE TABLE "USERS" (
	"ID"          INTEGER NOT NULL PRIMARY KEY ASC AUTOINCREMENT,
	"NAME"        TEXT    NOT NULL,
	"PASSWORD"    TEXT    NOT NULL,
	"PERMISSION"  INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS "IDX_NAME"       ON "USERS" ("NAME");
CREATE INDEX IF NOT EXISTS "IDX_PERMISSION" ON "USERS" ("PERMISSION");

/*
 * Create NICKS table with indizes on nickname (PK)
 */
CREATE TABLE "NICKNAMES" (
	"NICKNAME"    TEXT    NOT NULL,
	"USER_ID"     INTEGER NOT NULL,
	
	PRIMARY KEY ("NICKNAME"),
	FOREIGN KEY ("USER_ID") REFERENCES "USERS" ("ID")
);

/*
 * Create AUDITLOG table with indizes on 
 */
CREATE TABLE "AUDITLOG" (
    "ID"          INTEGER NOT NULL PRIMARY KEY ASC AUTOINCREMENT,
    "DATETIME"    TEXT    NOT NULL,
    "PRINCIPAL"   TEXT    NOT NULL,
    "ACTION"      TEXT    NOT NULL,
    "DATA_TYPE"   TEXT    NOT NULL,
    "DATA_BEFORE" TEXT    NULL,
    "DATA_AFTER"  TEXT    NULL
);

CREATE INDEX IF NOT EXISTS "IDX_ACTION" ON "AUDITLOG" ("ACTION");
CREATE INDEX IF NOT EXISTS "IDX_TYPE"   ON "AUDITLOG" ("DATA_TYPE");

/******************************************************************************/
/* calendar tables                                                            */
/******************************************************************************/

/*
 * Create CALENDARS table with indizes on ID (PK) and name
 */
CREATE TABLE "CALENDARS" (
	"ID"          INTEGER NOT NULL,
	"NAME"        TEXT    NOT NULL,
	"TYPE"        INTEGER NOT NULL,
	
	PRIMARY KEY ("ID")
);

CREATE INDEX IF NOT EXISTS "IDX_NAME" ON "CALENDARS" ("NAME");

/*
 * Create EVENTS table with indizes on ID (PK) and date
 */
CREATE TABLE "EVENTS" (
	"ID"          INTEGER NOT NULL,
	"CALENDAR_ID" INTEGER NOT NULL,
	"G_ETAG"      TEXT    NULL,
	"DATE_FROM"   TEXT    NOT NULL,
	"DATE_TO"     TEXT    NOT NULL,
	"DATE_ALLDAY" INTEGER NOT NULL,
	"DESCRIPTION" TEXT    NOT NULL,
	
	PRIMARY KEY ("ID"),
	FOREIGN KEY ("CALENDAR_ID") REFERENCES "CALENDARS" ("ID")
);

CREATE INDEX IF NOT EXISTS "IDX_ETAG" ON "EVENTS" ("G_ETAG");
CREATE INDEX IF NOT EXISTS "IDX_DATE" ON "EVENTS" ("DATE_FROM", "DATE_TO");

/*
 * Create CONTACTS table with indizes on firstname/lastname (PK) and birthday
 */
CREATE TABLE "CONTACTS" (
    "FIRSTNAME"   TEXT    NULL,
    "LASTNAME"    TEXT    NULL,
    "NICKNAME"    TEXT    NOT NULL,
    "BIRTHDAY"    TEXT    NOT NULL,
  
    PRIMARY KEY ("FIRSTNAME", "LASTNAME")
);

CREATE INDEX IF NOT EXISTS "IDX_BIRTHDAY" ON "CONTACTS" ("BIRTHDAY");

/*
 * Create BACKEND_MAPPING table with indizes on BACKEND, TYPE and LOCAL_ID
 */

CREATE TABLE "BACKEND_MAPPING" (
    "BACKEND"     TEXT    NOT NULL,
    "DATA_TYPE"   TEXT    NOT NULL,
    "LOCAL_ID"    INTEGER NOT NULL,
    "REMOTE_ID"   INTEGER NOT NULL,
    
    PRIMARY KEY ("BACKEND", "DATA_TYPE", "LOCAL_ID")
);

/******************************************************************************/
/* facts tables                                                               */
/******************************************************************************/

/*
 * Create FACTS table with indizes on DATE (PK)
 */
CREATE TABLE "FACTS" (
	"DATE" TEXT NOT NULL,
	"TEXT" TEXT NOT NULL,
	
	PRIMARY KEY ("DATE")
);

/******************************************************************************/
/* quotes tables                                                              */
/******************************************************************************/

/******************************************************************************/
/* topic tables                                                              */
/******************************************************************************/

/******************************************************************************/
/* stats tables                                                               */
/******************************************************************************/

/******************************************************************************/
/* game:bombkick tables                                                       */
/******************************************************************************/

/******************************************************************************/
/* game:sentence tables                                                       */
/******************************************************************************/
