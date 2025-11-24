DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS gas_cards;

CREATE TABLE IF NOT EXISTS vehicles (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	plate TEXT UNIQUE NOT NULL,
	insurance TEXT NOT NULL,
	inspection TEXT NOT NULL,
	maintenance TEXT NOT NULL,
	mileage TEXT DEFAULT 'no',
	status TEXT NOT NULL DEFAULT 'returned'
);

CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	is_identified INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS applications (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL,
	status TEXT NOT NULL DEFAULT 'pending',
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (username) REFERENCES users (username)
);

CREATE TABLE IF NOT EXISTS gas_cards (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	card_number TEXT UNIQUE NOT NULL,
	balance REAL DEFAULT 0.0,
	status TEXT NOT NULL DEFAULT 'returned'
);

-- Passwords table for admin-provisioned temporary passwords
CREATE TABLE IF NOT EXISTS passwords (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	password TEXT NOT NULL,
	status TEXT NOT NULL,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	used_at TIMESTAMP
);

-- Assignments track which password was issued for which resource(s)
CREATE TABLE IF NOT EXISTS assignments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	vehicle_id INTEGER,
	gas_card_id INTEGER,
	password TEXT,
	status TEXT NOT NULL,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated TIMESTAMP,
	FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
	FOREIGN KEY(gas_card_id) REFERENCES gas_cards(id)
);