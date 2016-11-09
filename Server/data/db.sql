CREATE Table ticket (
	id		INTEGER PRIMARY KEY AUTOINCREMENT,
	verifKey	TEXT NOT NULL,
	productType TEXT NOT NULL,
	availablePlaces INTEGER NOT NULL,
	totalPlaces INTEGER NOT NULL,
	validationDate	Datetime
);
