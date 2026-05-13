import re

KEYWORDS = {
    "SELECT",
    "FROM",
    "WHERE",
    "INSERT",
    "INTO",
    "VALUES",
    "CREATE",
    "TABLE",
    "UPDATE",
    "SET",
    "DELETE",
    "AND",
    "OR",
}

TOKEN_PATTERN = re.compile(
    r"\s*(>=|<=|!=|=|>|<|\*|,|\(|\)|;|\b[A-Za-z_][A-Za-z0-9_]*\b|\d+|'[^']*'|\"[^\"]*\")"
)


def tokenize(query: str):
    tokens = []
    for match in TOKEN_PATTERN.finditer(query):
        value = match.group(1)
        upper = value.upper()
        if upper in KEYWORDS:
            token_type = "KEYWORD"
        elif value in {"*", ",", "(", ")", ";"}:
            token_type = "PUNCTUATION"
        elif value in {"=", "!=", ">", "<", ">=", "<="}:
            token_type = "OPERATOR"
        elif re.fullmatch(r"\d+", value):
            token_type = "NUMBER"
        elif re.fullmatch(r"'[^']*'|\"[^\"]*\"", value):
            token_type = "STRING"
        else:
            token_type = "IDENTIFIER"
        tokens.append({"type": token_type, "value": value})
    return tokens
