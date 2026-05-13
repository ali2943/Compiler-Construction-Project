# Compiler-Construction-Project

## QueryLite Web

A mini SQL compiler demo that visualizes compiler phases for SQL-like queries.

### Project structure

- `/frontend`
  - `index.html`
  - `style.css`
  - `script.js`
- `/backend`
  - `app.py`
  - `lexer.py`
  - `parser.py`
  - `semantic.py`
  - `intermediate.py`
  - `optimizer.py`
  - `codegen.py`
  - `executor.py`
- `/tests`
  - `test_pipeline.py`

### Supported statements

- `CREATE TABLE`
- `INSERT`
- `SELECT`
- `UPDATE`
- `DELETE`
- `WHERE` with `AND/OR`

### Run locally

```bash
python -m backend.app
```

Open `http://127.0.0.1:5000`.

### API

`POST /run`

```json
{
  "query": "SELECT * FROM students;"
}
```

### Run tests

```bash
python -m unittest discover -s tests -v
```
