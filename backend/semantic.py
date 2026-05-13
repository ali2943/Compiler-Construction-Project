def _assert_table_exists(database, table):
    if table not in database:
        raise ValueError(f"Table '{table}' does not exist")


def _assert_columns_exist(database, table, columns):
    existing = set(database[table]["columns"])
    missing = [col for col in columns if col != "*" and col not in existing]
    if missing:
        raise ValueError(f"Unknown columns in table '{table}': {', '.join(missing)}")


def analyze(ast, database):
    statement = ast["type"]

    if statement == "CREATE_TABLE":
        if ast["table"] in database:
            raise ValueError(f"Table '{ast['table']}' already exists")
        return "Semantic check passed: CREATE TABLE is valid"

    table = ast["table"]
    _assert_table_exists(database, table)

    if statement == "INSERT":
        cols = ast["columns"] if ast["columns"] else database[table]["columns"]
        _assert_columns_exist(database, table, cols)
        if len(cols) != len(ast["values"]):
            raise ValueError("Column count does not match value count")
        return "Semantic check passed: INSERT is valid"

    if statement == "SELECT":
        _assert_columns_exist(database, table, ast["columns"])

    if statement == "UPDATE":
        _assert_columns_exist(database, table, list(ast["set"].keys()))

    where = ast.get("where")
    if where:
        _assert_columns_exist(database, table, [c["left"] for c in where["conditions"]])

    return f"Semantic check passed: {statement} is valid"
