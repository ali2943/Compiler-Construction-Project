import re
from typing import Dict, List

OPERATORS = [">=", "<=", "!=", "=", ">", "<"]


def _split_csv(text: str) -> List[str]:
    parts = []
    current = []
    in_quote = False
    quote_char = ""
    for ch in text:
        if ch in {"'", '"'}:
            if not in_quote:
                in_quote = True
                quote_char = ch
            elif quote_char == ch:
                in_quote = False
            current.append(ch)
        elif ch == "," and not in_quote:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


def _strip_value(value: str):
    v = value.strip()
    if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
        return v[1:-1]
    if re.fullmatch(r"\d+", v):
        return int(v)
    return v


def _parse_where(where_clause: str):
    if not where_clause:
        return None
    tokens = re.split(r"\s+(AND|OR)\s+", where_clause.strip(), flags=re.IGNORECASE)
    conditions = []
    connectors = []
    for index, chunk in enumerate(tokens):
        if index % 2 == 1:
            connectors.append(chunk.upper())
            continue
        condition_text = chunk.strip()
        op_found = None
        for op in OPERATORS:
            if op in condition_text:
                op_found = op
                break
        if not op_found:
            raise ValueError(f"Invalid WHERE condition: {condition_text}")
        left, right = condition_text.split(op_found, 1)
        conditions.append(
            {
                "left": left.strip(),
                "operator": op_found,
                "right": _strip_value(right.strip()),
            }
        )
    return {"conditions": conditions, "connectors": connectors}


def parse(query: str) -> Dict:
    cleaned = query.strip().rstrip(";")
    upper = cleaned.upper()

    create_match = re.match(r"^CREATE\s+TABLE\s+(\w+)\s*\((.+)\)$", cleaned, flags=re.IGNORECASE)
    if create_match:
        table = create_match.group(1)
        columns = [c.split()[0].strip() for c in _split_csv(create_match.group(2))]
        return {"type": "CREATE_TABLE", "table": table, "columns": columns}

    insert_match = re.match(
        r"^INSERT\s+INTO\s+(\w+)\s*(?:\(([^)]*)\))?\s+VALUES\s*\((.+)\)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if insert_match:
        table = insert_match.group(1)
        columns_text = insert_match.group(2)
        values_text = insert_match.group(3)
        columns = _split_csv(columns_text) if columns_text else []
        values = [_strip_value(v) for v in _split_csv(values_text)]
        return {"type": "INSERT", "table": table, "columns": columns, "values": values}

    select_match = re.match(
        r"^SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if select_match:
        cols = [c.strip() for c in _split_csv(select_match.group(1))]
        return {
            "type": "SELECT",
            "columns": cols,
            "table": select_match.group(2),
            "where": _parse_where(select_match.group(3) or ""),
        }

    update_match = re.match(
        r"^UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if update_match:
        assignments = {}
        for assign in _split_csv(update_match.group(2)):
            if "=" not in assign:
                raise ValueError(f"Invalid SET assignment: {assign}")
            key, value = assign.split("=", 1)
            assignments[key.strip()] = _strip_value(value)
        return {
            "type": "UPDATE",
            "table": update_match.group(1),
            "set": assignments,
            "where": _parse_where(update_match.group(3) or ""),
        }

    delete_match = re.match(
        r"^DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if delete_match:
        return {
            "type": "DELETE",
            "table": delete_match.group(1),
            "where": _parse_where(delete_match.group(2) or ""),
        }

    raise ValueError("Unsupported or invalid SQL statement")
