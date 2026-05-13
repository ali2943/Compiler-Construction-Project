import re


def _fold_condition(line):
    pattern = r"^t(\d+) = (\d+)\s*(>=|<=|!=|=|>|<)\s*(\d+)$"
    m = re.match(pattern, line)
    if not m:
        return line
    left = int(m.group(2))
    op = m.group(3)
    right = int(m.group(4))
    result = {
        ">": left > right,
        "<": left < right,
        "=": left == right,
        "!=": left != right,
        ">=": left >= right,
        "<=": left <= right,
    }[op]
    return f"t{m.group(1)} = {str(result)}"


def optimize(intermediate_lines):
    optimized = []
    previous = None
    for line in intermediate_lines:
        folded = _fold_condition(line)
        if folded == previous:
            continue
        optimized.append(folded)
        previous = folded
    return optimized
