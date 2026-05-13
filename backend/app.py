from copy import deepcopy
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from backend.codegen import generate_execution_steps
from backend.executor import build_symbol_table, execute
from backend.intermediate import generate as generate_intermediate
from backend.lexer import tokenize
from backend.optimizer import optimize
from backend.parser import parse
from backend.semantic import analyze

DEFAULT_DATABASE = {
    "students": {
        "columns": ["name", "age"],
        "rows": [
            {"name": "Alice", "age": 21},
            {"name": "Bob", "age": 18},
            {"name": "Charlie", "age": 24},
        ],
    }
}

DATABASE = deepcopy(DEFAULT_DATABASE)

frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app = Flask(__name__, static_folder=str(frontend_path), static_url_path="")


def reset_database():
    global DATABASE
    DATABASE = deepcopy(DEFAULT_DATABASE)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/run")
def run_query():
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        tokens = tokenize(query)
        ast = parse(query)
        semantic = analyze(ast, DATABASE)
        intermediate_code = generate_intermediate(ast)
        optimized_code = optimize(intermediate_code)
        code_generation = generate_execution_steps(optimized_code)
        output = execute(ast, DATABASE)
        symbol_table = build_symbol_table(DATABASE)
        return jsonify(
            {
                "tokens": tokens,
                "symbol_table": symbol_table,
                "semantic": semantic,
                "intermediate_code": intermediate_code,
                "optimized_code": optimized_code,
                "code_generation": code_generation,
                "output": output,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)
