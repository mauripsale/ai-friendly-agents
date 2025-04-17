#!/bin/bash
# sbrodola.sh - Generates the google_events.sqlite database

# Exit script on any error
set -e

# --- Configuration ---
# Use provided filename or default
DBFILE="${1:-google_events.sqlite}"
echo "--- Preparing database: $DBFILE ---"
echo "    (Dropping existing tables/triggers if they exist)"

# --- SQL Commands via Heredoc ---
sqlite3 "$DBFILE" <<EOF

-- ========================================================================== --
-- PRAGMAS & SETUP
-- ========================================================================== --

PRAGMA foreign_keys = ON;

-- ========================================================================== --
-- DROP EXISTING OBJECTS
-- ========================================================================== --

DROP TRIGGER IF EXISTS trigger_people_updated_at;
DROP TRIGGER IF EXISTS trigger_events_updated_at;
DROP TRIGGER IF EXISTS trigger_registrations_updated_at;

DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS people;


-- ========================================================================== --
-- CREATE TABLES
-- ========================================================================== --

-- Table: people
CREATE TABLE people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT CHECK( role IN ('SWE', 'SRE', 'PM', 'PSO', 'SA', 'DA', 'RE', 'UX', 'OTHER') ),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: events
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    event_date DATETIME NOT NULL,
    duration_hours REAL DEFAULT 2.0,
    capacity INTEGER,
    is_public BOOLEAN DEFAULT TRUE,       -- SQLite uses 0/1 for BOOLEAN
    ticket_price REAL DEFAULT 0.0,        -- <<< --- FIX: Added ticket_price column --- >>>
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, event_date)
);

-- Table: registrations
CREATE TABLE registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    registration_status TEXT CHECK( registration_status IN ('CONFIRMED', 'WAITLISTED', 'CANCELLED', 'ATTENDED') ) DEFAULT 'CONFIRMED',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES people (id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
    UNIQUE (person_id, event_id)
);


-- ========================================================================== --
-- CREATE TRIGGERS for updated_at timestamps
-- ========================================================================== --

CREATE TRIGGER trigger_people_updated_at AFTER UPDATE ON people FOR EACH ROW
BEGIN
    UPDATE people SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER trigger_events_updated_at AFTER UPDATE ON events FOR EACH ROW
BEGIN
    UPDATE events SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER trigger_registrations_updated_at AFTER UPDATE ON registrations FOR EACH ROW
BEGIN
    UPDATE registrations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;


-- ========================================================================== --
-- POPULATE TABLES WITH SAMPLE DATA
-- ========================================================================== --

-- Populate people table
INSERT INTO people (name, email, role) VALUES
('Claude Shannon', 'claude@bell.com', 'RE'),
('Vint Cerf', 'vint@google.com', 'RE'),
('Radia Perlman', 'radia@mit.edu', 'SWE'),
('Donald Knuth', 'knuth@stanford.edu', 'RE'),
('Sergey Brin', 'sergey@google.com', 'OTHER'),
('Larry Page', 'larry@google.com', 'OTHER'),
('Megan Smith', 'megan@example.com', 'PM'),
('Tim O''Reilly', 'tim@oreilly.com', 'OTHER'),
('Ada Colau', 'ada.colau@bcn.cat', 'OTHER'),
('Riccardo Carlesso', 'ricc@google.com', 'DA'),
('Daniel Aschwanden', 'ozzypvt@google.com', 'PSO'),
('Daniel Strebel', 'pvttutch@google.com', 'SA'),
('Mystery Guest', 'mystery@example.com', NULL);

-- Populate events table
-- Note: ticket_price is now the last value in the VALUES list
INSERT INTO events (name, location, event_date, duration_hours, capacity, is_public, ticket_price) VALUES
('Zurich Cloud Meetup Q2', 'Google ZRH BRL', '2025-05-15 18:30:00', 2.5, 120, 1, 0.0),
('Advanced Kubernetes Workshop', 'Online', '2025-06-10 09:00:00', 8.0, 40, 0, 499.99),
('Summer Tech BBQ', 'Google ZRH EML Garden', '2025-07-20 17:00:00', 4.0, 250, 1, 10.0),
('Intro to Vertex AI', 'Google ZRH Hürlimann', '2025-08-05 14:00:00', 3.0, 60, 1, 0.0),
('Data Science Switzerland Conf', 'ETH Hönggerberg', '2025-09-25 08:30:00', 16.0, NULL, 1, 150.0),
('Internal SRE Summit', 'Google ZRH BRL', '2025-10-15 10:00:00', 6.0, 80, 0, 0.0),
('GDG Cloud Zurich', 'Google ZRH EURx', '2025-04-24 10:00:00', 2.0, 80, 1, 0.0),
('GDG DevFaescht Zuri', 'Google ZRH EURB', '2025-10-10 10:00:00', 8.0, 100, 1, 0.0),
('GDG DevFest Modena', 'Laboratorio Aperto, Modena', '2025-10-04 10:00:00', 48.0, 400, 1, 0.0);

-- Populate registrations table
INSERT INTO registrations (person_id, event_id, registration_status) VALUES
(1, 4, 'CONFIRMED'),
(2, 1, 'CONFIRMED'), (2, 6, 'CONFIRMED'),
(3, 1, 'CONFIRMED'), (3, 5, 'ATTENDED'),
(4, 5, 'CONFIRMED'),
(5, 3, 'CONFIRMED'), (5, 6, 'WAITLISTED'),
(6, 3, 'CONFIRMED'),
(7, 1, 'CONFIRMED'), (7, 4, 'CONFIRMED'),

(10, 7, 'CONFIRMED'), (12, 7, 'CONFIRMED'), -- Ricc and Dan (the second dan is below)
(10, 8, 'CONFIRMED'), (11, 8, 'CONFIRMED'), (12, 8, 'CONFIRMED'), -- Ricc and Dan and Dan

(8, 5, 'ATTENDED'),
(10, 1, 'CONFIRMED'), (10, 2, 'CANCELLED'), (10, 3, 'CONFIRMED'), (10, 4, 'CONFIRMED'), (10, 5, 'WAITLISTED'),
(11, 7, 'ATTENDED');
-- Dan Ricc and Dan are 10,11,12 and should go to event GDG Zurich (7) and DevFaecht (8)

-- ========================================================================== --
-- EXAMPLE UPDATES (to test triggers)
-- ========================================================================== --
UPDATE people SET role = 'SWE' WHERE email = 'mystery@example.com';
UPDATE events SET location = 'Google ZRH EML (Main Hall)' WHERE id = 1;
UPDATE registrations SET registration_status = 'CONFIRMED' WHERE person_id = 10 AND event_id = 5;

EOF

echo ""
echo "--- Database '$DBFILE' created and populated successfully. ---"
echo ""
echo "Useful commands to try:"
echo "  sqlite3 $DBFILE '.schema'                               # Show schema"
echo "  sqlite3 $DBFILE '.tables'                               # List tables"
echo "  sqlite3 $DBFILE 'SELECT * FROM people LIMIT 5;'         # View some people"
echo "  sqlite3 $DBFILE 'SELECT * FROM events WHERE is_public=1;' # View public events"
echo "  sqlite3 $DBFILE -header -column 'SELECT p.name, e.name, r.registration_status FROM people p JOIN registrations r ON p.id=r.person_id JOIN events e ON r.event_id=e.id ORDER BY e.event_date, p.name;' # View registrations"
echo ""
