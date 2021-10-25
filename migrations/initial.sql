CREATE TABLE "criptobalance" (
	"id"	INTEGER NOT NULL UNIQUE,
	"date"	TEXT NOT NULL,
	"time"	TEXT NOT NULL,
	"coin_from"	TEXT NOT NULL,
	"quantity_from"	REAL NOT NULL,
	"coin_to"	TEXT NOT NULL,
	"quantity_to"	REAL NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)