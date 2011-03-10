/******************************************************************************/
/* General tables                                                             */
/******************************************************************************/

/*
 * Create CONFIG table with indizes on PACKGE and KEY (PK)
 */
CREATE TABLE "BOT_CONFIG" (
	"PACKAGE"     TEXT NOT NULL,
	"KEY"         TEXT NOT NULL,
	"VALUE"       TEXT NOT NULL,
	
	PRIMARY KEY ("PACKAGE", "KEY")
);

/*
 * Create USER table with indizes on ID (PK) and Name
 */
CREATE TABLE "BOT_USER" (
	"ID"          INTEGER NOT NULL PRIMARY KEY ASC AUTOINCREMENT,
	"NAME"        TEXT    NOT NULL,
	"PASSWORD"    TEXT    NOT NULL,
	"PERMISSION"  INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS "IDX_NAME"       ON "BOT_USER" ("NAME");
CREATE INDEX IF NOT EXISTS "IDX_PERMISSION" ON "BOT_USER" ("PERMISSION");

/*
 * Create NICKS table with indizes on ID (PK) and Name
 */
CREATE TABLE "BOT_NICKS" (
	"NICKNAME"    TEXT    NOT NULL PRIMARY KEY ASC,
	"USER_ID"     INTEGER NOT NULL,
	
	FOREIGN KEY ("USER_ID") REFERENCES "BOT_USER" ("ID")
);

/******************************************************************************/
/* calendar tables                                                            */
/******************************************************************************/

/*
 * Create CALENDAR table with indizes on ID (PK), Category, User and Name
 */
CREATE TABLE "CALENDAR_EVENTS" (
  "ID"          INTEGER NOT NULL PRIMARY KEY ASC AUTOINCREMENT,
  "CATEGORY_ID" INTEGER NOT NULL,
  "USER_ID"     INTEGER NULL,
  "NAME"        TEXT    NOT NULL,
  "DATE"        TEXT    NOT NULL,
  "REMINDED"    INTEGER NOT NULL,
	
  FOREIGN KEY ("CATEGORY_ID") REFERENCES "CALENDAR_CATEGORY" ("ID"),
  FOREIGN KEY ("USER_ID")     REFERENCES "BOT_USER" ("ID")
);

CREATE INDEX IF NOT EXISTS "IDX_CATEGORY" ON "CALENDAR_EVENTS" ("CATEGORY_ID");
CREATE INDEX IF NOT EXISTS "IDX_USER"     ON "CALENDAR_EVENTS" ("USER_ID");
CREATE INDEX IF NOT EXISTS "IDX_DATE"     ON "CALENDAR_EVENTS" ("DATE");

/*
 * Create CATEGORY table with indizes on ID (PK), User and Name
 */
CREATE TABLE "CALENDAR_CATEGORY" (
	"ID"      INTEGER NOT NULL PRIMARY KEY ASC AUTOINCREMENT,
	"USER_ID" INTEGER NULL,
	"NAME"    TEXT    NOT NULL,
	"COLOR"   TEXT    NOT NULL,
	"DEFAULT" INTEGER NOT NULL,

  FOREIGN KEY ("USER_ID") REFERENCES "BOT_USER" ("ID")
);

CREATE INDEX IF NOT EXISTS "IDX_USER" ON "CALENDAR_CATEGORY" ("USER_ID");
CREATE INDEX IF NOT EXISTS "IDX_NAME" ON "CALENDAR_CATEGORY" ("NAME");


/******************************************************************************/
/* facts tables                                                               */
/******************************************************************************/

/*
 * Create FACTS table with indizes on DATE (PK)
 */
CREATE TABLE "FACTS" (
	"DATE" TEXT NOT NULL PRIMARY KEY,
	"TEXT" TEXT NOT NULL
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
