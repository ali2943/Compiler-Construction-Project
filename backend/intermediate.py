def _condition_to_tac(where):
    if not where:
        return []
    lines = []
    temp_index = 1
    for condition in where["conditions"]:
        right = condition["right"]
        right_repr = f"'{right}'" if isinstance(right, str) else str(right)
        lines.append(f"t{temp_index} = {condition['left']} {condition['operator']} {right_repr}")
        temp_index += 1
    if where["connectors"]:
        combined = " t1 "
        for idx, connector in enumerate(where["connectors"], start=2):
            combined += f"{connector} t{idx} "
        lines.append(f"t{temp_index} = {combined.strip()}")
    return lines


def generate(ast):
    statement = ast["type"]
    lines = [f"BEGIN {statement}"]

    if statement == "CREATE_TABLE":
        lines.append(f"CREATE {ast['table']} COLUMNS {', '.join(ast['columns'])}")

    elif statement == "INSERT":
        columns = ast["columns"] if ast["columns"] else "ALL"
        lines.append(f"TARGET {ast['table']}")
        lines.append(f"COLUMNS {columns}")
        lines.append(f"VALUES {ast['values']}")

    elif statement == "SELECT":
        lines.append(f"SCAN {ast['table']}")
        lines.extend(_condition_to_tac(ast.get("where")))
        lines.append(f"PROJECT {ast['columns']}")

    elif statement == "UPDATE":
        lines.append(f"SCAN {ast['table']}")
        lines.extend(_condition_to_tac(ast.get("where")))
        lines.append(f"SET {ast['set']}")

    elif statement == "DELETE":
        lines.append(f"SCAN {ast['table']}")
        lines.extend(_condition_to_tac(ast.get("where")))
        lines.append("DELETE MATCHING")

    lines.append(f"END {statement}")
    return lines
