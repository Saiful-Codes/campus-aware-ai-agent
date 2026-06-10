import heapq
import os
import re
from typing import Dict, List, Optional, Tuple

import psycopg2

from app.services.postgres_service import open_postgres_connection


METERS_PER_GRID_STEP = 100.0

# Lightweight aliasing to resolve common campus wording without GIS complexity.
LOCATION_ALIASES: Dict[str, str] = {
    "dw": "dw",
    "donald whitehead": "dw",
    "donald whitehead building": "dw",
    "david wynter": "dw",
    "david wynter building": "dw",
    "david wynford smith": "dw",
    "tlc": "tlc",
    "the learning commons": "tlc",
    "library": "l",
    "borchardt library": "l",
    "agora": "a",
    "dmc": "dmc",
    "david myers": "dmc",
    "david myers building": "dmc",
}

NEAREST_FACILITY_PATTERNS: Dict[str, List[str]] = {
    "bathroom": ["bathroom", "toilet", "restroom", "washroom"],
    "library": ["library"],
    "lab": ["lab", "laboratory"],
    "study_space": ["study", "study space", "commons"],
}

FACILITY_TYPE_LABELS: Dict[str, str] = {
    "bathroom": "bathroom",
    "library": "library",
    "lab": "lab",
    "study_space": "study space",
}


def _open_pg_connection():
    return open_postgres_connection()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _apply_location_alias(term: str) -> str:
    normalized = _normalize(term)
    if normalized in LOCATION_ALIASES:
        return LOCATION_ALIASES[normalized]
    return normalized


def _extract_target_after_phrase(query: str, phrase: str) -> str:
    lowered = _normalize(query)
    if phrase not in lowered:
        return ""

    target = lowered.split(phrase, 1)[1].strip(" ?.!,:;")
    target = re.sub(r"^(the\s+)", "", target)
    return target.strip()


def _extract_route_points(query: str) -> Tuple[str, str]:
    lowered = _normalize(query)

    from_to = re.search(r"from\s+(.+?)\s+to\s+(.+?)(?:[?.!]|$)", lowered)
    if from_to:
        return from_to.group(1).strip(), from_to.group(2).strip()

    dest = _extract_target_after_phrase(lowered, "how do i get to")
    if not dest:
        dest = _extract_target_after_phrase(lowered, "how to get to")
    if not dest:
        dest = _extract_target_after_phrase(lowered, "directions to")
    if not dest:
        dest = _extract_target_after_phrase(lowered, "route to")
    if not dest:
        dest = _extract_target_after_phrase(lowered, "way to")

    # Default origin for demo routing if not explicitly provided.
    return "agora", dest


def _extract_requested_facility_type(query: str) -> Optional[str]:
    lowered = _normalize(query)
    for facility_type, aliases in NEAREST_FACILITY_PATTERNS.items():
        if any(alias in lowered for alias in aliases):
            return facility_type
    return None


def _extract_reference_location(query: str) -> str:
    lowered = _normalize(query)
    for pattern in [
        r"near(?:est)?\s+\w+\s+to\s+(.+?)(?:[?.!]|$)",
        r"near\s+(.+?)(?:[?.!]|$)",
        r"from\s+(.+?)(?:[?.!]|$)",
    ]:
        match = re.search(pattern, lowered)
        if match:
            return match.group(1).strip(" ?.!,:;")
    return ""


def _find_location(conn, raw_query: str) -> Optional[Dict[str, object]]:
    term = _apply_location_alias(raw_query)
    if not term:
        return None

    sql = """
        SELECT id, code, name, type, grid_ref, x_coord, y_coord, description,
               CASE
                   WHEN lower(code) = %s THEN 0
                   WHEN lower(name) = %s THEN 1
                   WHEN lower(name) LIKE %s THEN 2
                   WHEN lower(code) LIKE %s THEN 3
                   ELSE 4
               END AS rank
        FROM locations
        WHERE lower(name) LIKE %s OR lower(code) LIKE %s
        ORDER BY rank, length(name)
        LIMIT 1;
    """

    like_term = f"%{term}%"
    with conn.cursor() as cursor:
        cursor.execute(sql, (term, term, like_term, like_term, like_term, like_term))
        row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "code": row[1],
        "name": row[2],
        "type": row[3],
        "grid_ref": row[4],
        "x_coord": row[5],
        "y_coord": row[6],
        "description": row[7],
    }


def _find_nearest_facility(
    conn,
    facility_type: str,
    from_x: int,
    from_y: int,
) -> Optional[Dict[str, object]]:
    sql = """
        SELECT f.id, f.name, f.type, f.location_id, f.x_coord, f.y_coord, f.notes,
               l.name AS location_name,
               l.grid_ref,
               ((f.x_coord - %s)*(f.x_coord - %s) + (f.y_coord - %s)*(f.y_coord - %s)) AS dist_sq
        FROM facilities f
        JOIN locations l ON l.id = f.location_id
        WHERE f.type = %s
        ORDER BY dist_sq ASC
        LIMIT 1;
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (from_x, from_x, from_y, from_y, facility_type))
        row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "type": row[2],
        "location_id": row[3],
        "x_coord": row[4],
        "y_coord": row[5],
        "notes": row[6],
        "location_name": row[7],
        "grid_ref": row[8],
        "dist_sq": float(row[9]),
    }


def _cardinal_direction(from_x: int, from_y: int, to_x: int, to_y: int) -> str:
    dx = to_x - from_x
    dy = to_y - from_y

    if dx == 0 and dy == 0:
        return "straight"

    horizontal = ""
    vertical = ""

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
    return vertical or horizontal or "forward"


def _location_details_map(conn) -> Dict[int, Dict[str, object]]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, x_coord, y_coord FROM locations;")
        rows = cursor.fetchall()

    details: Dict[int, Dict[str, object]] = {}
    for row in rows:
        details[row[0]] = {
            "name": row[1],
            "x_coord": int(row[2]),
            "y_coord": int(row[3]),
        }
    return details


def _build_graph(conn) -> Dict[int, List[Tuple[int, float, str]]]:
    graph: Dict[int, List[Tuple[int, float, str]]] = {}
    details = _location_details_map(conn)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, from_location, to_location, distance, instruction
            FROM paths;
            """
        )
        rows = cursor.fetchall()

    for _, from_loc, to_loc, distance, instruction in rows:
        dist = float(distance or 0.0)
        instr = instruction or "Walk to the next campus point."

        graph.setdefault(from_loc, []).append((to_loc, dist, instr))

        # Treat path graph as bidirectional for practical directions.
        reverse_from = details.get(to_loc, {})
        reverse_to = details.get(from_loc, {})
        reverse_dir = _cardinal_direction(
            int(reverse_from.get("x_coord", 0)),
            int(reverse_from.get("y_coord", 0)),
            int(reverse_to.get("x_coord", 0)),
            int(reverse_to.get("y_coord", 0)),
        )
        reverse_instruction = (
            f"From {reverse_from.get('name', to_loc)}, walk {reverse_dir} toward "
            f"{reverse_to.get('name', from_loc)}."
        )
        graph.setdefault(to_loc, []).append((from_loc, dist, reverse_instruction))

    return graph


def _shortest_path(
    graph: Dict[int, List[Tuple[int, float, str]]],
    start: int,
    goal: int,
) -> Tuple[float, List[Tuple[int, int, str, float]]]:
    pq: List[Tuple[float, int]] = [(0.0, start)]
    distances: Dict[int, float] = {start: 0.0}
    previous: Dict[int, Tuple[int, str, float]] = {}

    while pq:
        current_dist, node = heapq.heappop(pq)
        if node == goal:
            break
        if current_dist > distances.get(node, float("inf")):
            continue

        for neighbor, edge_dist, instruction in graph.get(node, []):
            new_dist = current_dist + edge_dist
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                previous[neighbor] = (node, instruction, edge_dist)
                heapq.heappush(pq, (new_dist, neighbor))

    if goal not in distances:
        return float("inf"), []

    path: List[Tuple[int, int, str, float]] = []
    cursor = goal
    while cursor != start:
        prev_node, instruction, edge_dist = previous[cursor]
        path.append((prev_node, cursor, instruction, edge_dist))
        cursor = prev_node
    path.reverse()

    return distances[goal], path


def _location_name_map(conn) -> Dict[int, str]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name FROM locations;")
        return {row[0]: row[1] for row in cursor.fetchall()}


def answer_where_is_query(query: str) -> Tuple[str, str]:
    target = _extract_target_after_phrase(query, "where is")
    if not target:
        target = _extract_target_after_phrase(query, "where's")
    if not target:
        target = _extract_target_after_phrase(query, "location of")
    if not target:
        return (
            "I could not identify the destination. Please ask like: 'Where is the Library?'",
            "navigation_needs_target",
        )

    conn = None
    try:
        conn = _open_pg_connection()
        location = _find_location(conn, target)
    except Exception:
        return (
            "I couldn't access campus navigation data right now.",
            "navigation_db_error",
        )
    finally:
        if conn is not None:
            conn.close()

    if not location:
        return (
            f"I couldn't find '{target}' in the campus navigation data.",
            "navigation_not_found",
        )

    return (
        f"{location['name']} is located around grid {location['grid_ref']}, near x={location['x_coord']}, y={location['y_coord']}.",
        "navigation_where_success",
    )


def answer_nearest_query(query: str) -> Tuple[str, str]:
    facility_type = _extract_requested_facility_type(query)
    if not facility_type:
        return (
            "Please specify a facility type such as bathroom, library, or lab.",
            "navigation_nearest_needs_type",
        )

    reference_text = _extract_reference_location(query)
    conn = None
    try:
        conn = _open_pg_connection()
        origin = _find_location(conn, reference_text) if reference_text else None
        if not origin:
            origin = _find_location(conn, "agora")

        if not origin:
            return (
                "I couldn't determine a reference location for nearest search.",
                "navigation_nearest_no_origin",
            )

        nearest = _find_nearest_facility(conn, facility_type, origin["x_coord"], origin["y_coord"])
    except Exception:
        return (
            "I couldn't access campus navigation data right now.",
            "navigation_db_error",
        )
    finally:
        if conn is not None:
            conn.close()

    if not nearest:
        return (
            f"I couldn't find a '{facility_type}' entry in the current campus dataset.",
            "navigation_nearest_not_found",
        )

    facility_label = FACILITY_TYPE_LABELS.get(facility_type, facility_type.replace("_", " "))
    meters = round((nearest["dist_sq"] ** 0.5) * METERS_PER_GRID_STEP)
    return (
        f"The nearest {facility_label} is {nearest['name']} near {nearest['location_name']} (grid {nearest['grid_ref']}), approximately {meters} metres away.",
        "navigation_nearest_success",
    )


def answer_directions_query(query: str) -> Tuple[str, str]:
    origin_text, destination_text = _extract_route_points(query)
    if not destination_text:
        return (
            "I could not identify the destination. Please ask like: 'How do I get to TLC?'",
            "navigation_directions_needs_destination",
        )

    conn = None
    try:
        conn = _open_pg_connection()
        origin = _find_location(conn, origin_text)
        destination = _find_location(conn, destination_text)
        if not origin or not destination:
            return (
                "I couldn't match the origin or destination in the campus navigation data.",
                "navigation_directions_not_found",
            )

        graph = _build_graph(conn)
        total_distance, path_steps = _shortest_path(graph, origin["id"], destination["id"])
        id_to_name = _location_name_map(conn)
    except Exception:
        return (
            "I couldn't access campus navigation data right now.",
            "navigation_db_error",
        )
    finally:
        if conn is not None:
            conn.close()

    if not path_steps:
        return (
            f"I couldn't find a route from {origin['name']} to {destination['name']} in the current path graph.",
            "navigation_directions_no_path",
        )

    step_lines: List[str] = []
    for idx, (from_id, to_id, instruction, _) in enumerate(path_steps, start=1):
        from_name = id_to_name.get(from_id, str(from_id))
        to_name = id_to_name.get(to_id, str(to_id))
        step_lines.append(f"{idx}. {instruction} ({from_name} -> {to_name})")

    total_meters = round(total_distance)
    answer = (
        f"From {origin['name']} to {destination['name']}, follow these steps:\n"
        + "\n".join(step_lines)
        + f"\nEstimated distance: {total_meters} metres."
    )
    return answer, "navigation_directions_success"


def answer_navigation_query(intent: str, query: str) -> Tuple[str, str]:
    if intent == "navigation_where":
        return answer_where_is_query(query)

    if intent == "navigation_directions":
        return answer_directions_query(query)

    if intent == "navigation_nearest":
        return answer_nearest_query(query)

    return (
        "I couldn't map this request to a navigation action.",
        "navigation_unsupported_intent",
    )
