/******************************************************************************/
/* General tables                                                             */
/******************************************************************************/

/*
 * Create CONFIG table with indizes on PACKGE and KEY (PK)
 */
CREATE TABLE "CONFIGVALUES" (
	"PACKAGE"     TEXT NOT NULL,
	"KEY"         TEXT NOT NULL,
	"VALUE"       TEXT NOT NULL,
	
	PRIMARY KEY ("PACKAGE", "KEY")
);

/*
 * Create USER table with indizes on ID (PK) and Name
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
	"DESCRIPTION" TEXT    NOT NULL,
	"CREATED"     TEXT    NOT NULL,
	"CHANGED"     TEXT    NULL,
	
	PRIMARY KEY ("ID"),
	FOREIGN KEY ("CALENDAR_ID") REFERENCES "CALENDARS" ("ID")
);

CREATE INDEX IF NOT EXISTS "IDX_DATE" ON "EVENTS" ("DATE_FROM", "DATE_TO");

/*
 * Create CONTACTS table with indizes on firstname/lastname (PK) and birthday
 */
CREATE TABLE "CONTACTS" (
	"FIRST_NAME"  TEXT    NOT NULL,
	"LAST_NAME"   TEXT    NOT NULL,
	"BIRTHDAY"    TEXT    NOT NULL,
  
	PRIMARY KEY ("FIRST_NAME", "LAST_NAME")
);

CREATE INDEX IF NOT EXISTS "IDX_BIRTHDAY" ON "CONTACTS" ("BIRTHDAY");

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
