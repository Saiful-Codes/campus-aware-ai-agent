import logging
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psycopg2

from app.core.config import settings
from app.services.postgres_service import open_postgres_connection


logger = logging.getLogger(__name__)

METERS_PER_GRID_STEP = 100.0
AUTO_PATH_MAX_METERS = 230.0
AUTO_PATH_MAX_NEIGHBORS = 4


FULL_CAMPUS_LOCATIONS: List[Dict[str, str]] = [
    {"code": "A", "name": "Agora (University Centre - Food Court)", "type": "landmark", "grid_ref": "G6"},
    {"code": "AB", "name": "Agri Bio Building", "type": "building", "grid_ref": "L10"},
    {"code": "AE", "name": "Agora East", "type": "building", "grid_ref": "G6"},
    {"code": "AR", "name": "Agriculture Reserve", "type": "reserve", "grid_ref": "F1"},
    {"code": "AT", "name": "Agora Theatre and Cinema", "type": "lecture_theatre", "grid_ref": "G7"},
    {"code": "AW", "name": "Agora West", "type": "building", "grid_ref": "F6"},
    {"code": "BG", "name": "Beth Gleeson Building", "type": "building", "grid_ref": "E7"},
    {"code": "BNT", "name": "BioNTech (Under Construction)", "type": "building", "grid_ref": "E14"},
    {"code": "BS1", "name": "Biological Sciences 1", "type": "building", "grid_ref": "F5"},
    {"code": "BS2", "name": "Biological Sciences 2", "type": "building", "grid_ref": "E4"},
    {"code": "BST", "name": "Bus Terminus", "type": "transport", "grid_ref": "E6"},
    {"code": "BST-TB", "name": "Bus Stop - Toilet Block", "type": "transport", "grid_ref": "E6"},
    {"code": "CCO", "name": "Gatehouse", "type": "building", "grid_ref": "F10"},
    {"code": "CCR", "name": "Children's Centre", "type": "service", "grid_ref": "M8"},
    {"code": "CS1", "name": "Infrastructure and Operations", "type": "service", "grid_ref": "M5"},
    {"code": "CS2", "name": "Campus Services 2", "type": "service", "grid_ref": "M5"},
    {"code": "CS3", "name": "Landscaping", "type": "service", "grid_ref": "L5"},
    {"code": "CSCN", "name": "Cycle Smart Centre North", "type": "service", "grid_ref": "F5"},
    {"code": "CSCS", "name": "Cycle Smart Centre South", "type": "service", "grid_ref": "H7"},
    {"code": "DMC", "name": "David Myers Building - Centre", "type": "building", "grid_ref": "G8"},
    {"code": "DME", "name": "David Myers Building - East", "type": "building", "grid_ref": "H8"},
    {"code": "DMW", "name": "David Myers Building - West", "type": "building", "grid_ref": "F8"},
    {"code": "DW", "name": "Donald Whitehead Building", "type": "building", "grid_ref": "H6"},
    {"code": "ED1", "name": "Education 1", "type": "building", "grid_ref": "H8"},
    {"code": "ED2", "name": "Education 2", "type": "building", "grid_ref": "H8"},
    {"code": "ELT", "name": "East Lecture Theatres", "type": "lecture_theatre", "grid_ref": "H6"},
    {"code": "GC-AD", "name": "Glenn College - Admin", "type": "accommodation", "grid_ref": "J7"},
    {"code": "GS", "name": "George Singer Building", "type": "building", "grid_ref": "F4"},
    {"code": "HC", "name": "Health Clinic (Under Construction)", "type": "medical", "grid_ref": "D4"},
    {"code": "HS1", "name": "Health Sciences 1", "type": "building", "grid_ref": "D6"},
    {"code": "HS2", "name": "Health Sciences 2", "type": "building", "grid_ref": "D5"},
    {"code": "HS3", "name": "Health Sciences 3", "type": "building", "grid_ref": "D4"},
    {"code": "HSZ", "name": "Hooper and Szental Lecture Theatre", "type": "lecture_theatre", "grid_ref": "E8"},
    {"code": "HU2", "name": "Humanities 2", "type": "building", "grid_ref": "H7"},
    {"code": "HU3", "name": "Humanities 3", "type": "building", "grid_ref": "H7"},
    {"code": "ISC", "name": "Indoor Sports Centre", "type": "sports", "grid_ref": "L5"},
    {"code": "JG", "name": "Jenny Graves Building", "type": "building", "grid_ref": "F6"},
    {"code": "JSM", "name": "John Scott Meeting House", "type": "building", "grid_ref": "J5"},
    {"code": "L", "name": "Library", "type": "library", "grid_ref": "G5"},
    {"code": "LAN", "name": "La Trobe Apartment North", "type": "accommodation", "grid_ref": "L6"},
    {"code": "LAS", "name": "La Trobe Apartment South", "type": "accommodation", "grid_ref": "L7"},
    {"code": "LIMS1", "name": "La Trobe Institute for Molecular Science 1", "type": "building", "grid_ref": "F5"},
    {"code": "LIMS2", "name": "La Trobe Institute for Molecular Science 2", "type": "building", "grid_ref": "E6"},
    {"code": "LPFP", "name": "Lower Playing Field Pavilion", "type": "sports", "grid_ref": "A12"},
    {"code": "LTPH", "name": "La Trobe Private Hospital", "type": "medical", "grid_ref": "C1"},
    {"code": "LTSS", "name": "La Trobe Sports Stadium", "type": "sports", "grid_ref": "B8"},
    {"code": "MAR", "name": "Martin Building", "type": "building", "grid_ref": "H6"},
    {"code": "MC", "name": "Menzies College", "type": "accommodation", "grid_ref": "J8"},
    {"code": "MCA1-5", "name": "Menzies College Annexe", "type": "accommodation", "grid_ref": "J9"},
    {"code": "MC-AD", "name": "Menzies College - Admin", "type": "accommodation", "grid_ref": "J8"},
    {"code": "MT", "name": "Moat Theatre", "type": "lecture_theatre", "grid_ref": "I9"},
    {"code": "NTWS-BS", "name": "Nangak Tamboree Wildlife Sanctuary - Bioshack", "type": "reserve", "grid_ref": "K2"},
    {"code": "NTWS-IBH", "name": "Nangak Tamboree Wildlife Sanctuary - Ironbark Hut", "type": "reserve", "grid_ref": "L1"},
    {"code": "NTWS-LC", "name": "Nangak Tamboree Wildlife Sanctuary - Learning Centre", "type": "reserve", "grid_ref": "J1"},
    {"code": "NTWS-VC", "name": "Nangak Tamboree Wildlife Sanctuary - Visitor Centre", "type": "reserve", "grid_ref": "J1"},
    {"code": "PE", "name": "Peribolos East", "type": "building", "grid_ref": "G8"},
    {"code": "PS1", "name": "Physical Sciences 1", "type": "building", "grid_ref": "F7"},
    {"code": "PS2", "name": "Physical Sciences 2", "type": "building", "grid_ref": "G7"},
    {"code": "PW", "name": "Peribolos West", "type": "building", "grid_ref": "F7"},
    {"code": "RD3", "name": "CARM Centre", "type": "external", "grid_ref": "N10"},
    {"code": "RD4", "name": "Victoria Police", "type": "external", "grid_ref": "O12"},
    {"code": "RLR", "name": "R.L. Reid Building", "type": "building", "grid_ref": "E5"},
    {"code": "SP", "name": "Sports Park", "type": "sports", "grid_ref": "C11"},
    {"code": "SPP", "name": "Sports Park Pavilion", "type": "sports", "grid_ref": "A10"},
    {"code": "SS", "name": "Social Sciences", "type": "building", "grid_ref": "H5"},
    {"code": "SW", "name": "Sylvia Walton Building", "type": "building", "grid_ref": "I8"},
    {"code": "TER9-14", "name": "The Terraces Building 9 to 14", "type": "building", "grid_ref": "P7"},
    {"code": "TLC", "name": "The Learning Commons", "type": "study_space", "grid_ref": "F6"},
    {"code": "U", "name": "Union Building", "type": "building", "grid_ref": "H9"},
    {"code": "UCC", "name": "La Trobe Lifeskills", "type": "service", "grid_ref": "J9"},
    {"code": "USF", "name": "Urban Solar Farm", "type": "infrastructure", "grid_ref": "B4"},
    {"code": "WLT", "name": "West Lecture Theatres", "type": "lecture_theatre", "grid_ref": "D5"},
    {"code": "ZR", "name": "Zoology Reserve", "type": "reserve", "grid_ref": "H1"},
    {"code": "CC1-12", "name": "Chisholm College (Blocks 1 to 12)", "type": "accommodation", "grid_ref": "G11"},
    {"code": "GC", "name": "Glenn College", "type": "accommodation", "grid_ref": "K6"},
]


def _open_pg_connection():
    return open_postgres_connection()


def _parse_grid_ref(grid_ref: str) -> Tuple[Optional[int], Optional[int]]:
    match = re.match(r"\s*([A-Z])\s*(\d+)", (grid_ref or "").upper())
    if not match:
        return None, None
    x = ord(match.group(1)) - ord("A") + 1
    y = int(match.group(2))
    return x, y


def _direction_word(from_x: int, from_y: int, to_x: int, to_y: int) -> str:
    dx = to_x - from_x
    dy = to_y - from_y

    vertical = ""
    horizontal = ""

    if dy > 0:
        vertical = "north"
    elif dy < 0:
        vertical = "south"

    if dx > 0:
        horizontal = "east"
    elif dx < 0:
        horizontal = "west"

    if vertical and horizontal:
        return f"{vertical}-{horizontal}"
    return vertical or horizontal or "straight"


def _upsert_full_location_catalog(conn) -> int:
    upserted = 0
    with conn.cursor() as cursor:
        for item in FULL_CAMPUS_LOCATIONS:
            x, y = _parse_grid_ref(item["grid_ref"])
            if x is None or y is None:
                continue

            cursor.execute(
                """
                UPDATE locations
                SET name = %s,
                    type = %s,
                    grid_ref = %s,
                    x_coord = %s,
                    y_coord = %s,
                    description = %s
                WHERE lower(code) = lower(%s);
                """,
                (
                    item["name"],
                    item["type"],
                    item["grid_ref"],
                    x,
                    y,
                    f"Campus map node: {item['name']}",
                    item["code"],
                ),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO locations (code, name, type, grid_ref, x_coord, y_coord, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        item["code"],
                        item["name"],
                        item["type"],
                        item["grid_ref"],
                        x,
                        y,
                        f"Campus map node: {item['name']}",
                    ),
                )
            upserted += 1

    return upserted


def _seed_auto_paths(conn) -> int:
    # IDs 1-15 are reserved for curated manual paths from SQL seed.
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM paths WHERE id > 15;")

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, x_coord, y_coord
            FROM locations
            WHERE x_coord IS NOT NULL AND y_coord IS NOT NULL;
            """
        )
        rows = cursor.fetchall()

    locations = [
        {"id": int(row[0]), "name": str(row[1]), "x": int(row[2]), "y": int(row[3])}
        for row in rows
    ]

    with conn.cursor() as cursor:
        cursor.execute("SELECT from_location, to_location FROM paths;")
        existing_rows = cursor.fetchall()

    existing_pairs = {
        (min(int(a), int(b)), max(int(a), int(b))) for a, b in existing_rows if a != b
    }

    generated_pairs: Dict[Tuple[int, int], Tuple[float, str]] = {}
    by_id = {loc["id"]: loc for loc in locations}

    for loc in locations:
        neighbor_candidates: List[Tuple[float, Dict[str, int]]] = []
        for other in locations:
            if loc["id"] == other["id"]:
                continue
            dx = other["x"] - loc["x"]
            dy = other["y"] - loc["y"]
            distance_m = math.sqrt((dx * dx) + (dy * dy)) * METERS_PER_GRID_STEP
            if distance_m <= AUTO_PATH_MAX_METERS:
                neighbor_candidates.append((distance_m, other))

        neighbor_candidates.sort(key=lambda item: item[0])

        for distance_m, other in neighbor_candidates[:AUTO_PATH_MAX_NEIGHBORS]:
            pair = (min(loc["id"], other["id"]), max(loc["id"], other["id"]))
            if pair in existing_pairs or pair in generated_pairs:
                continue

            from_node = by_id[pair[0]]
            to_node = by_id[pair[1]]
            direction = _direction_word(from_node["x"], from_node["y"], to_node["x"], to_node["y"])
            instruction = f"From {from_node['name']}, walk {direction} toward {to_node['name']}."
            generated_pairs[pair] = (round(distance_m, 1), instruction)

    all_pairs = set(existing_pairs) | set(generated_pairs.keys())

    adjacency: Dict[int, set] = {loc["id"]: set() for loc in locations}
    for a, b in all_pairs:
        adjacency[a].add(b)
        adjacency[b].add(a)

    def _collect_components() -> List[List[int]]:
        seen = set()
        components: List[List[int]] = []
        for node in adjacency:
            if node in seen:
                continue
            stack = [node]
            seen.add(node)
            comp: List[int] = []
            while stack:
                current = stack.pop()
                comp.append(current)
                for nxt in adjacency[current]:
                    if nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)
            components.append(comp)
        return components

    while True:
        components = _collect_components()
        if len(components) <= 1:
            break

        best_bridge: Optional[Tuple[int, int, float]] = None
        for left_idx in range(len(components)):
            for right_idx in range(left_idx + 1, len(components)):
                for left_id in components[left_idx]:
                    for right_id in components[right_idx]:
                        left = by_id[left_id]
                        right = by_id[right_id]
                        dx = right["x"] - left["x"]
                        dy = right["y"] - left["y"]
                        distance_m = math.sqrt((dx * dx) + (dy * dy)) * METERS_PER_GRID_STEP
                        if best_bridge is None or distance_m < best_bridge[2]:
                            best_bridge = (left_id, right_id, distance_m)

        if best_bridge is None:
            break

        left_id, right_id, distance_m = best_bridge
        pair = (min(left_id, right_id), max(left_id, right_id))
        if pair not in all_pairs:
            from_node = by_id[pair[0]]
            to_node = by_id[pair[1]]
            direction = _direction_word(from_node["x"], from_node["y"], to_node["x"], to_node["y"])
            generated_pairs[pair] = (
                round(distance_m, 1),
                f"From {from_node['name']}, walk {direction} toward {to_node['name']}.",
            )
            all_pairs.add(pair)
            adjacency[left_id].add(right_id)
            adjacency[right_id].add(left_id)

    inserted = 0
    with conn.cursor() as cursor:
        for (from_id, to_id), (distance_m, instruction) in generated_pairs.items():
            cursor.execute(
                """
                INSERT INTO paths (from_location, to_location, distance, instruction)
                VALUES (%s, %s, %s, %s);
                """,
                (from_id, to_id, distance_m, instruction),
            )
            inserted += 1

    return inserted


def _bootstrap_sql_path() -> Path:
    return Path(__file__).resolve().parents[1] / "db" / "campus_navigation_bootstrap.sql"


def bootstrap_navigation_data() -> Tuple[int, int, int]:
    sql_path = _bootstrap_sql_path()
    if not sql_path.exists():
        raise FileNotFoundError(f"Navigation bootstrap SQL not found: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")

    conn = _open_pg_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)

        upserted_nodes = _upsert_full_location_catalog(conn)
        inserted_paths = _seed_auto_paths(conn)
        conn.commit()

        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM locations;")
            locations_count = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM facilities;")
            facilities_count = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM paths;")
            paths_count = int(cursor.fetchone()[0])

        logger.info(
            "Navigation catalog refresh complete: upserted_nodes=%s, auto_paths_inserted=%s",
            upserted_nodes,
            inserted_paths,
        )
    finally:
        conn.close()

    return locations_count, facilities_count, paths_count


def ensure_navigation_data_ready() -> None:
    try:
        locations_count, facilities_count, paths_count = bootstrap_navigation_data()
        logger.info(
            "Navigation data ready: %s locations, %s facilities, %s paths",
            locations_count,
            facilities_count,
            paths_count,
        )
    except Exception as exc:
        logger.warning("Navigation bootstrap skipped or failed: %s", exc)
