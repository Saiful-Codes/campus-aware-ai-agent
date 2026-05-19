-- Minimal campus navigation dataset derived from Melbourne Inner Campus Map PDF
-- Source: data/sample_pdfs/Melbourne-Inner-Campus-Map.pdf
-- Note: Some entries are marked approximate where the map label is clear but exact point placement is not explicit.

-- ============================================
-- 1) SCHEMA
-- ============================================

DROP TABLE IF EXISTS paths;
DROP TABLE IF EXISTS facilities;
DROP TABLE IF EXISTS locations;

CREATE TABLE locations (
  id SERIAL PRIMARY KEY,
  code VARCHAR(20),
  name VARCHAR(100),
  type VARCHAR(50),
  grid_ref VARCHAR(10),
  x_coord INT,
  y_coord INT,
  description TEXT
);

CREATE TABLE facilities (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  type VARCHAR(50), -- bathroom, lab, library, study_space
  location_id INT REFERENCES locations(id),
  x_coord INT,
  y_coord INT,
  notes TEXT
);

CREATE TABLE paths (
  id SERIAL PRIMARY KEY,
  from_location INT REFERENCES locations(id),
  to_location INT REFERENCES locations(id),
  distance FLOAT,
  instruction TEXT
);

-- ============================================
-- 2) LOCATIONS (16 entries; high-value subset)
-- Grid conversion: A=1 ... Z=26, number => y
-- ============================================

INSERT INTO locations (id, code, name, type, grid_ref, x_coord, y_coord, description) VALUES
(1, 'L', 'Library', 'library', 'G5', 7, 5, 'Library and ASK La Trobe services (map-listed).'),
(2, 'A', 'Agora', 'landmark', 'G6', 7, 6, 'University Centre and food court; central navigation hub.'),
(3, 'AE', 'Agora East', 'building', 'G6', 7, 6, 'Eastern side of Agora precinct.'),
(4, 'AW', 'Agora West', 'building', 'F6', 6, 6, 'Western side of Agora precinct.'),
(5, 'AT', 'Agora Theatre and Cinema', 'landmark', 'G7', 7, 7, 'Lecture/cinema area in Agora precinct.'),
(6, 'TLC', 'The Learning Commons', 'study_space', 'F6', 6, 6, 'Major student study and learning area.'),
(7, 'DW', 'Donald Whitehead Building', 'building', 'H6', 8, 6, 'Major teaching building.'),
(8, 'ELT', 'East Lecture Theatres', 'building', 'H6', 8, 6, 'Cluster of lecture theatres (ELT1-ELT6).'),
(9, 'DMC', 'David Myers Building - Centre', 'building', 'G8', 7, 8, 'Central DMC entry area.'),
(10, 'MAR', 'Martin Building', 'building', 'H6', 8, 6, 'Teaching and lecture spaces.'),
(11, 'JG', 'Jenny Graves Building', 'building', 'F6', 6, 6, 'Student services, innovation hubs, and accessibility services.'),
(12, 'LIMS1', 'La Trobe Institute for Molecular Science 1', 'building', 'F5', 6, 5, 'Molecular science facilities (map-listed).'),
(13, 'LIMS2', 'La Trobe Institute for Molecular Science 2', 'building', 'E6', 5, 6, 'Molecular science facilities (map-listed).'),
(14, 'BST', 'Bus Terminus', 'transport', 'E6', 5, 6, 'Primary bus interchange near inner campus core (approximate).'),
(15, 'BST-TB', 'Bus Stop - Toilet Block', 'transport', 'E6', 5, 6, 'Toilet block beside bus stop (map-listed).'),
(16, 'PCP2', 'Parking Area PCP2', 'parking', 'G4', 7, 4, 'Designated car parking area near inner campus core (approximate).');

-- Keep SERIAL sequence aligned after explicit IDs
SELECT setval('locations_id_seq', (SELECT MAX(id) FROM locations));

-- ============================================
-- 3) FACILITIES (10 entries)
-- 3 bathrooms, 3 labs, 1 library, 3 study spaces
-- ============================================

INSERT INTO facilities (id, name, type, location_id, x_coord, y_coord, notes) VALUES
(1, 'Library Ground Floor Restrooms', 'bathroom', 1, 7, 5, 'Approximate; restroom access in Library precinct.'),
(2, 'Agora Central Restrooms', 'bathroom', 2, 7, 6, 'Approximate; restroom access in Agora area.'),
(3, 'Bus Stop Toilet Block', 'bathroom', 15, 5, 6, 'Map-listed as BST-TB.'),
(4, 'Education Practice Lab', 'lab', 1, 7, 5, 'Map-listed in Library description (Level 2).'),
(5, 'Digital Innovation Hub', 'lab', 11, 6, 6, 'Listed under student services in JG building.'),
(6, 'Molecular Science Teaching Lab', 'lab', 12, 6, 5, 'Approximate lab point inside LIMS1 precinct.'),
(7, 'Library Service Point', 'library', 1, 7, 5, 'Primary library service and information point.'),
(8, 'TLC Study Zone', 'study_space', 6, 6, 6, 'Open study area in TLC.'),
(9, 'Agora Study Commons', 'study_space', 2, 7, 6, 'Informal study area near Agora central zone (approximate).'),
(10, 'Library Quiet Study Area', 'study_space', 1, 7, 5, 'Quiet study area in Library precinct (approximate).');

SELECT setval('facilities_id_seq', (SELECT MAX(id) FROM facilities));

-- ============================================
-- 4) PATH GRAPH (15 paths)
-- Distances are simplified for demo use and mostly coordinate-based approximations.
-- ============================================

INSERT INTO paths (id, from_location, to_location, distance, instruction) VALUES
(1, 1, 2, 100.0, 'From the Library, walk north toward the Agora.'),
(2, 2, 6, 100.0, 'From the Agora, continue west to reach The Learning Commons.'),
(3, 6, 7, 200.0, 'From The Learning Commons, walk east to the Donald Whitehead Building.'),
(4, 7, 8, 40.0, 'Within the same precinct, continue to East Lecture Theatres.'),
(5, 2, 9, 200.0, 'From the Agora, walk north along the main pedestrian route to DMC.'),
(6, 9, 10, 224.0, 'From DMC, head southeast to the Martin Building.'),
(7, 2, 11, 100.0, 'From the Agora, walk west to the Jenny Graves Building.'),
(8, 11, 12, 100.0, 'From JG, walk south to LIMS1.'),
(9, 12, 13, 141.0, 'From LIMS1, walk southwest to LIMS2.'),
(10, 13, 14, 60.0, 'From LIMS2, continue to the Bus Terminus zone.'),
(11, 14, 15, 40.0, 'At the Bus Terminus, move to the nearby Toilet Block.'),
(12, 2, 16, 200.0, 'From the Agora, walk south toward Parking Area PCP2.'),
(13, 2, 7, 120.0, 'From the Agora, walk east to the Donald Whitehead Building.'),
(14, 7, 9, 224.0, 'From the Donald Whitehead Building, head north-west to DMC.'),
(15, 6, 9, 224.0, 'From The Learning Commons, walk north-east to DMC.');

SELECT setval('paths_id_seq', (SELECT MAX(id) FROM paths));

-- ============================================
-- 5) EXAMPLE QUERY SUPPORT
-- ============================================

-- WHERE IS X
SELECT *
FROM locations
WHERE name ILIKE '%library%'
   OR code ILIKE '%L%';

-- NEAREST FACILITY (example point x=7,y=6)
SELECT f.*, l.name AS location_name,
       ((f.x_coord - 7)*(f.x_coord - 7) + (f.y_coord - 6)*(f.y_coord - 6)) AS dist_sq
FROM facilities f
JOIN locations l ON l.id = f.location_id
ORDER BY dist_sq ASC
LIMIT 1;

-- NEAREST FACILITY BY TYPE (example: bathroom)
SELECT f.*, l.name AS location_name,
       ((f.x_coord - 7)*(f.x_coord - 7) + (f.y_coord - 6)*(f.y_coord - 6)) AS dist_sq
FROM facilities f
JOIN locations l ON l.id = f.location_id
WHERE f.type = 'bathroom'
ORDER BY dist_sq ASC
LIMIT 1;

-- DIRECTIONS: immediate next steps from a location
SELECT p.id, lf.name AS from_name, lt.name AS to_name, p.distance, p.instruction
FROM paths p
JOIN locations lf ON lf.id = p.from_location
JOIN locations lt ON lt.id = p.to_location
WHERE p.from_location = 1
ORDER BY p.id;

-- Optional recursive traversal for multi-hop route expansion can be added later.

-- ============================================
-- 6) SAMPLE CHATBOT RESPONSE FORMAT
-- Gemini should format responses from DB results only.
-- ============================================

-- WHERE IS X
-- "{X} is located near {nearest_landmark}, around grid {grid_ref}."

-- DIRECTIONS
-- "From {A}, walk toward {landmark}, then continue to {B}. Estimated distance: {distance_m} metres."

-- NEAREST
-- "The nearest {facility_type} is located near {building_name}, approximately {distance_m} metres away."
