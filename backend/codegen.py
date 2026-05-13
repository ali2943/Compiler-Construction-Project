def generate_execution_steps(optimized_lines):
    steps = []
    for index, line in enumerate(optimized_lines, start=1):
        steps.append(f"Step {index}: {line}")
    return steps
