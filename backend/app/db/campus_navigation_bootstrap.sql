-- Idempotent bootstrap for campus navigation data.
-- Safe to run multiple times.

CREATE TABLE IF NOT EXISTS locations (
  id SERIAL PRIMARY KEY,
  code VARCHAR(20),
  name VARCHAR(100),
  type VARCHAR(50),
  grid_ref VARCHAR(10),
  x_coord INT,
  y_coord INT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS facilities (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  type VARCHAR(50),
  location_id INT REFERENCES locations(id),
  x_coord INT,
  y_coord INT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS paths (
  id SERIAL PRIMARY KEY,
  from_location INT REFERENCES locations(id),
  to_location INT REFERENCES locations(id),
  distance FLOAT,
  instruction TEXT
);

-- Locations (16)
INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 1, 'L', 'Library', 'library', 'G5', 7, 5, 'Library and ASK La Trobe services (map-listed).'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 1);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 2, 'A', 'Agora', 'landmark', 'G6', 7, 6, 'University Centre and food court; central navigation hub.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 2);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 3, 'AE', 'Agora East', 'building', 'G6', 7, 6, 'Eastern side of Agora precinct.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 3);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 4, 'AW', 'Agora West', 'building', 'F6', 6, 6, 'Western side of Agora precinct.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 4);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 5, 'AT', 'Agora Theatre and Cinema', 'landmark', 'G7', 7, 7, 'Lecture/cinema area in Agora precinct.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 5);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 6, 'TLC', 'The Learning Commons', 'study_space', 'F6', 6, 6, 'Major student study and learning area.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 6);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 7, 'DW', 'Donald Whitehead Building', 'building', 'H6', 8, 6, 'Major teaching building.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 7);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 8, 'ELT', 'East Lecture Theatres', 'building', 'H6', 8, 6, 'Cluster of lecture theatres (ELT1-ELT6).'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 8);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 9, 'DMC', 'David Myers Building - Centre', 'building', 'G8', 7, 8, 'Central DMC entry area.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 9);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 10, 'MAR', 'Martin Building', 'building', 'H6', 8, 6, 'Teaching and lecture spaces.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 10);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 11, 'JG', 'Jenny Graves Building', 'building', 'F6', 6, 6, 'Student services, innovation hubs, and accessibility services.'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 11);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 12, 'LIMS1', 'La Trobe Institute for Molecular Science 1', 'building', 'F5', 6, 5, 'Molecular science facilities (map-listed).'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 12);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 13, 'LIMS2', 'La Trobe Institute for Molecular Science 2', 'building', 'E6', 5, 6, 'Molecular science facilities (map-listed).'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 13);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 14, 'BST', 'Bus Terminus', 'transport', 'E6', 5, 6, 'Primary bus interchange near inner campus core (approximate).'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 14);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 15, 'BST-TB', 'Bus Stop - Toilet Block', 'transport', 'E6', 5, 6, 'Toilet block beside bus stop (map-listed).'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 15);

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description)
SELECT 16, 'PCP2', 'Parking Area PCP2', 'parking', 'G4', 7, 4, 'Designated car parking area near inner campus core (approximate).'
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id = 16);

-- Facilities (10)
INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 1, 'Library Ground Floor Restrooms', 'bathroom', 1, 7, 5, 'Approximate; restroom access in Library precinct.'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 1);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 2, 'Agora Central Restrooms', 'bathroom', 2, 7, 6, 'Approximate; restroom access in Agora area.'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 2);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 3, 'Bus Stop Toilet Block', 'bathroom', 15, 5, 6, 'Map-listed as BST-TB.'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 3);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 4, 'Education Practice Lab', 'lab', 1, 7, 5, 'Map-listed in Library description (Level 2).'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 4);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 5, 'Digital Innovation Hub', 'lab', 11, 6, 6, 'Listed under student services in JG building.'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 5);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 6, 'Molecular Science Teaching Lab', 'lab', 12, 6, 5, 'Approximate lab point inside LIMS1 precinct.'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 6);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 7, 'Library Service Point', 'library', 1, 7, 5, 'Primary library service and information point.'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 7);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 8, 'TLC Study Zone', 'study_space', 6, 6, 6, 'Open study area in TLC.'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 8);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 9, 'Agora Study Commons', 'study_space', 2, 7, 6, 'Informal study area near Agora central zone (approximate).'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 9);

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes)
SELECT 10, 'Library Quiet Study Area', 'study_space', 1, 7, 5, 'Quiet study area in Library precinct (approximate).'
WHERE NOT EXISTS (SELECT 1 FROM facilities WHERE id = 10);

-- Paths (15)
INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 1, 1, 2, 100.0, 'From the Library, walk north toward the Agora.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 1);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 2, 2, 6, 100.0, 'From the Agora, continue west to reach The Learning Commons.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 2);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 3, 6, 7, 200.0, 'From The Learning Commons, walk east to the Donald Whitehead Building.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 3);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 4, 7, 8, 40.0, 'Within the same precinct, continue to East Lecture Theatres.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 4);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 5, 2, 9, 200.0, 'From the Agora, walk north along the main pedestrian route to DMC.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 5);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 6, 9, 10, 224.0, 'From DMC, head southeast to the Martin Building.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 6);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 7, 2, 11, 100.0, 'From the Agora, walk west to the Jenny Graves Building.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 7);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 8, 11, 12, 100.0, 'From JG, walk south to LIMS1.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 8);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 9, 12, 13, 141.0, 'From LIMS1, walk southwest to LIMS2.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 9);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 10, 13, 14, 60.0, 'From LIMS2, continue to the Bus Terminus zone.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 10);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 11, 14, 15, 40.0, 'At the Bus Terminus, move to the nearby Toilet Block.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 11);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 12, 2, 16, 200.0, 'From the Agora, walk south toward Parking Area PCP2.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 12);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 13, 2, 7, 120.0, 'From the Agora, walk east to the Donald Whitehead Building.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 13);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 14, 7, 9, 224.0, 'From the Donald Whitehead Building, head north-west to DMC.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 14);

INSERT INTO paths (id, from_location, to_location, distance, instruction)
SELECT 15, 6, 9, 224.0, 'From The Learning Commons, walk north-east to DMC.'
WHERE NOT EXISTS (SELECT 1 FROM paths WHERE id = 15);

SELECT setval('locations_id_seq', COALESCE((SELECT MAX(id) FROM locations), 1));
SELECT setval('facilities_id_seq', COALESCE((SELECT MAX(id) FROM facilities), 1));
SELECT setval('paths_id_seq', COALESCE((SELECT MAX(id) FROM paths), 1));
