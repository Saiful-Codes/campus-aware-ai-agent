def is_safe_select_query(sql_query: str) -> bool:
    """
    Allow only safe SELECT queries on sensor_readings.
    Blocks INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, etc.
    """

    if not sql_query:
        return False

    query = sql_query.strip().lower()

    blocked_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant",
        "revoke",
        "replace",
    ]

    if not query.startswith("select"):
        return False

    if "sensor_readings" not in query:
        return False

    for keyword in blocked_keywords:
        if keyword in query:
            return False

    return True