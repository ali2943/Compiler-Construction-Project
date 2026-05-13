
def _compare(left, operator, right):
    if operator == "=":
        return left == right
    if operator == "!=":
        return left != right
    if operator == ">":
        return left > right
    if operator == "<":
        return left < right
    if operator == ">=":
        return left >= right
    if operator == "<=":
        return left <= right
    return False


def _matches_where(row, where):
    if not where:
        return True
    bools = []
    for condition in where["conditions"]:
        left = row.get(condition["left"])
        right = condition["right"]
        if isinstance(left, int) and isinstance(right, str) and right.isdigit():
            right = int(right)
        bools.append(_compare(left, condition["operator"], right))

    result = bools[0] if bools else True
    for idx, connector in enumerate(where["connectors"], start=1):
        if connector == "AND":
            result = result and bools[idx]
        else:
            result = result or bools[idx]
    return result


def execute(ast, database):
    statement = ast["type"]
    table_name = ast.get("table")

    if statement == "CREATE_TABLE":
        database[ast["table"]] = {"columns": ast["columns"], "rows": []}
        return f"Table '{ast['table']}' created"

    table = database[table_name]

    if statement == "INSERT":
        columns = ast["columns"] if ast["columns"] else table["columns"]
        row = {col: None for col in table["columns"]}
        for col, val in zip(columns, ast["values"]):
            row[col] = val
        table["rows"].append(row)
        return "1 row inserted"

    if statement == "SELECT":
        selected_rows = [r for r in table["rows"] if _matches_where(r, ast.get("where"))]
        cols = table["columns"] if ast["columns"] == ["*"] else ast["columns"]
        projected = [{col: row.get(col) for col in cols} for row in selected_rows]
        return {"row_count": len(projected), "rows": projected}

    if statement == "UPDATE":
        updated = 0
        for row in table["rows"]:
            if _matches_where(row, ast.get("where")):
                for key, value in ast["set"].items():
                    row[key] = value
                updated += 1
        return f"{updated} row(s) updated"

    if statement == "DELETE":
        kept = []
        deleted = 0
        for row in table["rows"]:
            if _matches_where(row, ast.get("where")):
                deleted += 1
            else:
                kept.append(row)
        table["rows"] = kept
        return f"{deleted} row(s) deleted"

    raise ValueError("Unsupported statement for execution")


def build_symbol_table(database):
    symbols = {}
    for table_name, table in database.items():
        symbols[table_name] = {
            "columns": table["columns"],
            "row_count": len(table["rows"]),
            "values": table["rows"],
        }
    return symbols
