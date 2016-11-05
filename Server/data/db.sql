CREATE Table ticket (
	id		INTEGER PRIMARY KEY AUTOINCREMENT,
	verifKey	TEXT UNIQUE NOT NULL,
	availablePlaces INTEGER NOT NULL,
	totalPlaces INTEGER NOT NULL,
	validationDate	Datetime
);
